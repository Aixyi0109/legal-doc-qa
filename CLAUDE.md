# CLAUDE.md - legal-doc-qa

## 语言约定

**全程使用中文回答。** 无论代码注释、报错分析、解释说明，一律中文。不得切换为韩文、英文或其他语言（代码本身除外）。

## 这是什么项目

基于 RAG 的法律文档问答系统。Day 4 开始,目标 Day 14 完成 v1。

这是简历主打项目之一,不是 demo。要求工程质量、可观测、可演示。

## 我目前的进度

- ✅ Day 4:目录结构、架构图、PDFParser、UnstructuredParser、/upload 接口、简单 chunker
- 🚧 Day 5:embedding + Chroma 集成(进行中)
- ⏳ Day 6:端到端跑通 + demo 视频
- ⏳ Day 8-14:Eval、Reranker、Docker、部署

## 技术栈

- Python 3.11 + uv 包管理(不要建议我用 pip)
- FastAPI(异步路由)
- pypdf + unstructured(双 parser 策略)
- bge-m3(本地 embedding,通过 sentence-transformers)
- Chroma(持久化路径 ./chroma_db)
- DeepSeek API(生成)
- pytest(测试)

## 目录约定

```
app/
  api/         FastAPI 路由
  core/        配置、日志
  ingestion/   parser + chunker + embedder + store(文档摄入)
  retrieval/   检索逻辑
  generation/  prompt + LLM 调用
  models/      Pydantic 模型
tests/         pytest
docs/          架构图、设计决策(decisions.md、iteration-log.md)
data/          测试 PDF(进 .gitignore,不上传)
docker/        Dockerfile + docker-compose
```

## 关键设计决策(我已经做的)

1. **Parser 用策略模式**:PDFParser + UnstructuredParser 同接口,可切换
2. **Chunker 先手写再用 LangChain**:理解 RecursiveCharacterTextSplitter 的本质
3. **每个 chunk 带 metadata**(source_file、page、chunk_index):为后期多文档过滤铺路
4. **配置用 pydantic-settings,不用 os.getenv**

如果你的建议违反上面任何一条,先问我"是否要改变这个决策",不要直接改。

## 我的水平 / 你对我的行为

我是 LLM/Agent 学习者(Day X / 60)。请遵守全局 CLAUDE.md 里的"code-tutor 行为约束":

- 不要直接给完整代码
- 先问我的思路
- 逐行解释 + 检验问题
- 用 🟢🟡🔴 标记复杂度
- 错误优先教学
- 用 Conventional Commits 写 commit message

## 当前 Phase 的优先级

**Week 2(Day 8-14)我要做的事,按优先级:**

1. 🔴 Eval 系统:20 个测试问题,baseline → v2 → v3 准确率追踪
2. 🔴 Reranker(bge-reranker)集成
3. 🟡 多文档独立检索(metadata 过滤)
4. 🟡 Docker 化
5. 🟢 Streamlit 前端
6. 🟢 部署到云服务器

如果我问你不在上面优先级里的事(比如"我想加 GraphRAG"、"要不要换 Qdrant"),**先提醒我这是 scope creep,问我是不是真的需要**。

## 我容易犯的错(提前提醒我)

- **过度封装**:看到一个东西想加抽象基类、工厂模式 → 阻止我
- **教程仔病**:抄 LangChain 教程不思考 → 阻止我,强迫我先讲设计
- **不写 Eval**:做完功能想跳过 eval 直接上下一个 → 阻止我
- **不写注释**:Day 1-3 我留下的代码很多没注释 → Day 5 起我开始补

## 测试我的命令(每次重要改动后)

```bash
uv run pytest                              # 单元测试
uv run uvicorn app.main:app --reload       # 启动服务
```

## 我会经常问你的问题类型(预设应对)

| 我说 | 你做 |
|------|------|
| "这个分块策略合理吗" | 先反问我为什么这么选,再给建议 |
| "RAG 准确率怎么提高" | 先列 5 个可能维度,让我选先做哪个 |
| "帮我加 XX 功能" | 先输出 plan,我 review 再写 |
| "Day X 完成" | 进入 interview-coach 模式,问我 4 个开放式问题 |
| "这个 bug 不会修" | 先问我尝试了什么,不要直接给修复 |
