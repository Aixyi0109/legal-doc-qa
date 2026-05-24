# Legal Doc QA

基于 RAG 的中文法律文档问答系统。输入法律文件（PDF），问任意问题，返回答案 + 页码来源。

## 当前进度

- ✅ Day 4：目录结构、PDFParser、UnstructuredParser、`/upload` 接口、FixedLengthChunker
- ✅ Day 5：LangChain Chunker、Embedder（bge-m3）、VectorStore（Chroma）、IngestionPipeline 端到端跑通
- 🚧 Day 6：检索接口 + DeepSeek 生成 + 端到端问答

## 架构

```
POST /upload
  │
  ├─ PDFParser          → list[dict]  {"page": N, "text": "..."}
  ├─ Chunker            → list[dict]  + chunk_id, chunk_index
  ├─ Embedder (bge-m3)  → list[dict]  + embedding
  └─ VectorStore        → Chroma 持久化（含 source_file、page、chunk_index）

POST /query  (待实现)
  │
  ├─ Embedder           → 查询向量
  ├─ Chroma 检索        → top-k chunks
  └─ DeepSeek           → 生成答案 + 引用页码
```

## 项目结构

```
legal-doc-qa/
├── app/
│   ├── api/            # FastAPI 路由（upload.py）
│   ├── core/           # 配置、日志
│   ├── ingestion/      # parser / chunker / embedder / store / pipeline
│   ├── retrieval/      # 检索逻辑（待实现）
│   ├── generation/     # Prompt + LLM 调用（待实现）
│   └── models/         # Pydantic 模型
├── scripts/
│   └── test_pipeline.py  # 端到端摄入测试
├── tests/              # pytest 单元测试
├── docs/               # 设计决策（decisions.md）
├── data/               # 测试用 PDF（gitignored）
└── docker/
```

## 如何运行

### 环境准备

```bash
# 安装依赖
uv sync

# 配置环境变量（复制模板后填入 API Key）
cp .env.example .env
```

### 端到端摄入（PDF → Chroma）

```bash
# 首次运行会自动下载 bge-m3 模型（约 2.3GB）
PYTHONPATH=. uv run python scripts/test_pipeline.py
```

### 启动服务

```bash
uv run uvicorn app.main:app --reload
```

服务启动后访问 http://localhost:8000/docs 查看接口文档。

### 上传 PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@data/民法典.pdf"
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
| 文本分块 | LangChain RecursiveCharacterTextSplitter |
| Embedding | BAAI/bge-m3（sentence-transformers） |
| 向量数据库 | Chroma（持久化至 ./chroma_db） |
| 生成模型 | DeepSeek API（待接入） |
| 包管理 | uv |
