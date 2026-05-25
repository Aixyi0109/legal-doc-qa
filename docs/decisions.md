# 设计决策记录

> 记录关键技术选型的原因，方便日后回顾或向面试官解释。

---

## 为什么选 pypdf

**决策**：文档解析默认使用 `pypdf`，而非 `pdfminer`、`pdfplumber` 或 `unstructured`。

**原因**：
- `pypdf` 零依赖、安装快，适合项目早期快速验证
- API 简单：`PdfReader(path)` → 逐页 `.extract_text()`，10 行内跑通
- 对结构规整的法律文档（民法典）效果足够好

**代价**：
- 无法识别扫描版 PDF（需要 OCR）
- 对复杂排版（多列、表格）提取效果差
- 不保留字体、段落等结构信息

**后续升级路径**：如果遇到扫描版或排版复杂的合同，切换到 `unstructured[pdf]`（已在 `parser.py` 里预留了 `UnstructuredParser` 类）。

---

## 为什么 parser 返回 `list[dict]` 而不是 `str`

**决策**：`PDFParser.parse()` 返回 `[{"page": 1, "text": "..."}, ...]`，而不是直接拼接成一个大字符串。

**原因**：

1. **保留页码信息**：RAG 回答时需要引用来源（"见第 28 条，位于第 10 页"），如果提前拼成字符串，页码信息就丢了。

2. **灵活性**：下游模块（chunker、embedder）可以按需处理——既可以逐页分块，也可以合并后再分块，调用方来决定。

3. **可扩展**：`UnstructuredParser` 在 dict 里多加了 `"category"` 字段（`Title`、`NarrativeText` 等），结构统一，切换解析器不需要改下游代码。

**反例**：如果返回 `str`，调用方就永远不知道某段文字在第几页，溯源功能无法实现。

---

## 为什么 chunk 带三个 metadata 字段

**决策**：每个 chunk 存入 Chroma 时携带 `source_file`、`page`、`chunk_index` 三个 metadata 字段。

**原因**：

1. **`source_file`**：支持多文档场景。日后系统里有多份合同时，可以按文件过滤检索，不会把不同文档的内容混在一起回答。
2. **`page`**：RAG 回答需要精确引用（"见第 10 页第 28 条"），法律场景不能没有出处。
3. **`chunk_index`**：全局唯一编号，方便调试（"第 42 块内容是什么"）和后期 Eval 时追踪具体 chunk 的检索命中情况。

**代价**：`add()` 需要多传几个字段，代码稍复杂，但值得。

**相关代码**：`app/ingestion/pipeline.py`（注入 `source_file`）、`app/ingestion/chunker.py`（生成 `chunk_index`）、`app/ingestion/store.py`（写入 metadatas）。

---

## 为什么用 bge-m3 而不是 bge-large-zh 或 m3e-base

**决策**：Embedding 模型选 `BAAI/bge-m3`。

**原因**：

1. **长文档支持**：bge-m3 最大输入 8192 tokens；bge-large-zh 和 m3e-base 上限是 512 tokens，民法典单条款就可能超限。
2. **多语言**：法律文档里有英文术语、数字，bge-m3 覆盖 100+ 语言，不需要担心混合语言的 embedding 质量下降。
3. **社区活跃**：BAAI 持续维护，文档完整，sentence-transformers 原生支持。

**代价**：模型较大（约 2.3GB），首次运行需要下载，冷启动慢。生产环境应在服务启动时预加载（FastAPI lifespan）。

---

## 为什么先手写 chunker 再用 LangChain

**决策**：自己实现 `FixedLengthChunker`，而不是直接用 `LangChain` 的 `RecursiveCharacterTextSplitter`。

**原因**：

1. **搞清楚原理**：LangChain 的 splitter 背后也是在做字符遍历 + 边界判断，先手写一遍，面试时才能解释"chunk_size 和 overlap 在做什么"，而不是只会调 API。

2. **中文特殊性**：LangChain 默认按字符数切，对中文文档来说空白符会占用大量配额。手写版实现了 `chunk_by_hanzi`（只计汉字数），更适合中文法律文档。

3. **调试方便**：遇到切割效果不好时，手写版可以直接改逻辑；用 LangChain 则需要先查文档找对应参数。

**何时切换到 LangChain**：需要语义分块（按句子、段落边界切）或者 `MarkdownHeaderTextSplitter` 等高级功能时，再引入 LangChain。

---

## 为什么流式接口用 SSE 而不是 WebSocket

**决策**：`/query/stream` 使用 SSE（Server-Sent Events），而非 WebSocket。

**原因**：

1. **单向推送**：LLM 生成是单向的——服务端推 token 给客户端，客户端不需要在流的过程中发消息回来。SSE 天然匹配这个模型，WebSocket 的双工能力在这里是浪费。

2. **基于 HTTP**：SSE 基于标准 HTTP/1.1，不需要协议升级握手。可以穿透大多数防火墙和反向代理，不需要特殊配置。

3. **自动重连**：浏览器原生支持 SSE 断线自动重连（`EventSource` API），WebSocket 断线重连需要客户端自己写逻辑。

4. **实现更简单**：FastAPI 用 `StreamingResponse(generate(), media_type="text/event-stream")` 即可，不需要引入 `websockets` 依赖。

**代价**：只支持单向推送，如果未来需要"用户打断生成"（类似 ChatGPT 停止按钮）这类双向交互，需要换成 WebSocket 或单独的 HTTP 取消接口。

**SSE 帧格式**：
- 普通 token：`data: {内容}\n\n`
- 特殊事件：`event: sources\ndata: {...}\n\n`（最后一帧，携带引用来源）

---

## 为什么用 FastAPI lifespan 预加载模型

**决策**：在 `main.py` 的 `lifespan` 上下文管理器里初始化 `Embedder`（bge-m3）和 `Generator`（DeepSeek 客户端），而不是在每次请求时创建。

**原因**：

1. **冷启动成本**：bge-m3 模型约 2.3GB，每次请求都加载会导致第一次调用耗时 30–60 秒。lifespan 保证应用启动时只加载一次。

2. **共享连接**：DeepSeek 的 `OpenAI` 客户端内部维护连接池，全局单例可以复用连接，减少 TCP 握手开销。

3. **FastAPI 推荐模式**：官方文档明确推荐用 `lifespan` 替代已废弃的 `@app.on_event("startup")`，代码更清晰，生命周期更可预测。

**实现**：所有共享对象挂在 `app.state` 上，路由通过 `request.app.state.xxx` 访问，避免全局变量。

---

## 为什么 Generator 把 prompt 构建抽成 `_build_message`

**决策**：`Generator` 类里 `generate()` 和 `generate_stream()` 共用一个私有方法 `_build_message()` 来构建 prompt。

**原因**：

1. **DRY 原则**：两个方法的唯一区别是 `stream=True/False`，prompt 构建逻辑完全一样。如果复制粘贴，改一处忘改另一处，会产生 bug。

2. **单一职责**：`generate()` 只负责调用 API + 返回完整文本，`generate_stream()` 只负责逐 token yield，prompt 的组装属于独立关注点。

3. **Python 约定**：`_build_message` 的 `_` 前缀表示"内部实现细节，外部不应直接调用"，是 Python 的私有方法约定（非强制，但团队共识）。

**prompt 设计选择**：系统 prompt 里包含检索到的 chunks（`第N页，来源文件X\n{text}`），并明确告知"如果文档中没有相关信息，回答'根据提供的文档信息，无法回答该问题'"——主动限制幻觉，适合法律场景对准确性的高要求。

---

## 为什么 RAGPipeline.query() 同时返回 answer 和 sources

**决策**：`RAGPipeline.query()` 返回 `{"answer": ..., "sources": [...]}` 而非只返回 `answer`。

**原因**：

1. **引用来源是 RAG 的核心价值**：用户问法律问题，需要知道答案来自哪一页、哪份文件，才能核实。只返回 answer 是不完整的。

2. **避免二次检索**：如果 API 层需要 sources，必须在 pipeline 层一次性传出来。否则要么 API 层自己再检索一次（浪费），要么 sources 永远拿不到。

3. **流式版统一处理**：`query_stream()` 先 yield 所有 token，最后一帧 yield `{"type": "sources", "data": retrieved_chunks}`，保证流结束后客户端能拿到引用。
