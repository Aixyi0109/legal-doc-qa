# Legal Doc QA

基于 RAG 的法律文档问答系统。

## 架构

![架构图](docs/architecture.png)

## 项目结构

```
legal-doc-qa/
├── app/
│   ├── api/         # FastAPI 路由
│   ├── core/        # 配置、日志
│   ├── ingestion/   # 文档解析 + 分块 + 入库
│   ├── retrieval/   # 检索逻辑
│   ├── generation/  # Prompt + LLM 调用
│   └── models/      # Pydantic 模型
├── tests/
├── docs/            # 架构图、设计文档
├── data/            # 测试用 PDF
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

### 启动服务

```bash
uv run uvicorn main:app --reload
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
