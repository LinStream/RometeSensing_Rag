# 学习文档：参考 agent.zip 结构版 RAG 项目

## 1. 你先看什么

推荐顺序：

```text
1. README.md
2. config/rag.yml
3. config/chroma.yml
4. model/factory.py
5. rag/vector_store.py
6. rag/rag_service.py
7. backend/app/api/rag.py
8. frontend/streamlit_app.py
```

## 2. 本项目和 agent.zip 的关系

你给的项目是一个 Streamlit + Agent 项目，其中 RAG 部分主要在：

```text
model/factory.py
rag/vector_store.py
rag/rag_service.py
utils/
config/
prompts/
```

我这版主要就是保留这些设计，只把前端后端拆成：

```text
Streamlit 前端
FastAPI 后端
```

## 3. RAG 核心链路

```text
用户上传 PDF/TXT
↓
FastAPI 保存到 data/
↓
RagSummarizeService.load_single_file()
↓
VectorStoreService.load_single_file()
↓
pdf_loader / txt_loader
↓
RecursiveCharacterTextSplitter
↓
Chroma.add_documents()
↓
DashScopeEmbeddings 自动向量化
```

用户提问：

```text
Streamlit 输入问题
↓
POST /api/rag/ask
↓
RagSummarizeService.rag_summarize_with_sources()
↓
VectorStoreService.get_retriever()
↓
Chroma 检索
↓
PromptTemplate 拼接 input + context
↓
ChatTongyi 生成回答
↓
StrOutputParser 输出字符串
↓
FastAPI 返回 answer + sources
↓
Streamlit 展示
```

## 4. 重点文件解释

### 4.1 model/factory.py

作用：创建模型。

```python
ChatTongyi(model=rag_conf["chat_model_name"])
DashScopeEmbeddings(model=rag_conf["embedding_model_name"])
```

配置来自：

```text
config/rag.yml
```

### 4.2 rag/vector_store.py

作用：管理向量库。

主要内容：

```text
Chroma
RecursiveCharacterTextSplitter
md5 去重
load_single_file()
load_document()
get_retriever()
```

### 4.3 rag/rag_service.py

作用：管理 RAG 问答流程。

核心链：

```python
self.prompt_template | print_prompt | self.model | StrOutputParser()
```

这和你给的项目保持一致。

### 4.4 backend/app/api/rag.py

作用：把 RAG 服务包装成 FastAPI 接口。

例如：

```python
@router.post("/ask")
def ask(req: AskRequest):
    result = rag_service.rag_summarize_with_sources(...)
```

### 4.5 frontend/streamlit_app.py

作用：页面展示和调用后端接口。

核心还是：

```python
requests.post(...)
requests.get(...)
requests.delete(...)
```

## 5. 你后面怎么继续升级

建议下一步加：

```text
1. MySQL 保存上传文件信息
2. MySQL 保存问答历史
3. 支持删除单个文档
4. 支持按文档过滤检索
5. 加 Agent 工具调用，把 rag_summarize 作为 tool
```
