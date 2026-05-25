# Legal Doc QA

基于 RAG 的中文法律文档问答系统。输入法律文件（PDF），问任意问题，返回答案 + 页码来源。

## 当前进度

- ✅ Day 4：目录结构、PDFParser、UnstructuredParser、`/upload` 接口、FixedLengthChunker
- ✅ Day 5：LangChain Chunker、Embedder（bge-m3）、VectorStore（Chroma）、IngestionPipeline 端到端跑通
- ✅ Day 6：Retriever、Generator（DeepSeek）、RAGPipeline、`/upload` 全链路、`/query`、`/query/stream`（SSE）
- ⏳ Day 7-14：Eval、Reranker、Docker、部署

## 架构

```
POST /upload
  │
  ├─ PDFParser          → list[dict]  {"page": N, "text": "..."}
  ├─ Chunker            → list[dict]  + chunk_id, chunk_index
  ├─ Embedder (bge-m3)  → list[dict]  + embedding
  └─ VectorStore        → Chroma 持久化（含 source_file、page、chunk_index）
  返回: {"filename": "...", "pages": N, "chunks": N}

POST /query
  │
  ├─ Retriever          → embed query → Chroma top-k chunks
  └─ Generator          → DeepSeek prompt → answer + 页码引用
  返回: {"answer": "...", "sources": [...]}

POST /query/stream      （SSE）
  │
  ├─ Retriever          → top-k chunks
  ├─ Generator          → stream tokens  →  data: token\n\n
  └─ 最后一条           →  event: sources\ndata: [...]\n\n
```

## 项目结构

```
legal-doc-qa/
├── main.py             # FastAPI 入口 + lifespan（模型预加载）
├── app/
│   ├── api/            # 路由（upload.py、query.py）
│   ├── ingestion/      # parser / chunker / embedder / store / pipeline
│   ├── retrieval/      # retriever.py
│   ├── generation/     # generator.py / pipeline.py（RAGPipeline）
│   ├── models/         # Pydantic 模型（schemas.py）
│   └── core/           # 配置、日志（待完善）
├── scripts/
│   └── test_pipeline.py  # 端到端摄入测试
├── tests/              # pytest 单元测试
├── docs/               # decisions.md、iteration-log.md
├── data/               # 测试用 PDF（gitignored）
└── docker/
```

## 如何运行

### 环境准备

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env    # 填入 DEEPSEEK_API_KEY
```

### 启动服务

```bash
# 首次启动会自动下载 bge-m3（约 2.3GB），需要等几分钟
PYTHONPATH=. uv run uvicorn main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看接口文档。

### 上传 PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@data/民法典.pdf"
# 返回: {"filename": "民法典.pdf", "pages": 176, "chunks": 561}
```

### 问答查询

```bash
# 普通接口
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "合同解除的条件是什么", "source_file": "民法典.pdf"}'

# 流式接口（SSE）
curl -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "合同解除的条件是什么", "source_file": "民法典.pdf"}'
```

### 运行测试

```bash
uv run pytest tests/ -v
```

## 技术栈

| 层 | 技术 |
|---|---|
| Web 框架 | FastAPI + uvicorn |
| PDF 解析 | pypdf（默认）/ unstructured（扫描件） |
| 文本分块 | LangChain RecursiveCharacterTextSplitter（chunk_size=300） |
| Embedding | BAAI/bge-m3（sentence-transformers） |
| 向量数据库 | Chroma（持久化至 ./chroma_db） |
| 生成模型 | DeepSeek API（deepseek-chat） |
| 包管理 | uv |
