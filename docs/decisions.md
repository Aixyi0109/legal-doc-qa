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
