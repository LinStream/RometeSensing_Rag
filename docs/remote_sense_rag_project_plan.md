# 遥感资料智能问答系统：项目规划与实现思路文档

## 0. 文档目的

这份文档不是代码说明书，而是**项目规划文档**。

它回答的是：

```text
这个项目整体应该长什么样？
应该有哪些功能？
每个功能应该放在哪一层？
每个功能大概怎么实现？
先做什么，后做什么？
怎么从 demo 变成简历项目？
```

你现在的问题不是不会某个 API，而是知识比较零散：

```text
会一点 FastAPI
会一点 Streamlit
会一点 LangChain
知道 RAG
知道 Chroma
知道 embedding
知道大模型调用
```

但是暂时还缺少：

```text
项目架构视角
模块拆分能力
功能规划能力
从 0 到 1 做项目的路线感
```

所以这份文档重点帮你建立一个完整项目的思路。

---

# 1. 项目定位

项目名称可以暂定为：

```text
RemoteSense-RAG：遥感资料智能问答与学习助手系统
```

项目定位：

```text
面向遥感专业学习、考研复习、论文阅读、真题整理的领域知识库问答系统。
```

用户可以上传：

```text
遥感教材
遥感原理资料
南大真题
复习笔记
论文 PDF
项目文档
```

系统完成：

```text
文档解析
文本切分
向量化入库
知识库检索
RAG 问答
来源片段展示
问答历史保存
文档管理
```

最终目标：

```text
不是做一个玩具 PDF 问答 Demo，
而是做一个可以写进简历的 AI 应用后端项目。
```

---

# 2. 项目核心价值

这个项目适合你，是因为它同时结合了：

```text
1. 你的遥感专业背景
2. 你正在转向 Agent / AI 应用开发
3. 你已经学过 FastAPI
4. 你正在学 RAG / LangChain
5. 后续可以扩展 MySQL、Redis、Docker
```

它比普通“通用 PDF 问答系统”更有特色：

```text
别人：通用文档问答
你：遥感领域知识库问答与学习助手
```

这个“领域特色”很重要。

---

# 3. 总体架构图

## 3.1 当前最小架构

```text
┌────────────────────────────┐
│            用户             │
│  上传 PDF / 输入问题        │
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│        Streamlit 前端       │
│  文件上传 / 提问 / 展示结果 │
└──────────────┬─────────────┘
               │ HTTP 请求
               ▼
┌────────────────────────────┐
│        FastAPI 后端         │
│  Router / Schema / Service  │
└──────────────┬─────────────┘
               │ 调用业务服务
               ▼
┌────────────────────────────┐
│         RAG Service         │
│  解析 / 切分 / 检索 / 生成   │
└───────┬──────────────┬─────┘
        │              │
        ▼              ▼
┌──────────────┐ ┌────────────────┐
│ Chroma 向量库 │ │  百炼大模型服务 │
│ 存储/检索向量 │ │ Embedding/Chat  │
└──────────────┘ └────────────────┘
```

---

## 3.2 简历项目目标架构

```text
┌──────────────────────────────────────┐
│                前端层                 │
│ Streamlit / 后续可替换 Vue 或 React   │
│ 上传文档 / 提问 / 文档列表 / 历史记录 │
└──────────────────┬───────────────────┘
                   │ HTTP
                   ▼
┌──────────────────────────────────────┐
│                API 层                 │
│ FastAPI Router                        │
│ rag / documents / chat / users        │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│              Service 层               │
│ RAGService                            │
│ DocumentService                       │
│ ChatService                           │
│ VectorStoreService                    │
└──────────┬───────────────┬───────────┘
           │               │
           ▼               ▼
┌────────────────┐   ┌────────────────┐
│    Model 层     │   │   Vector 层     │
│ ChatTongyi      │   │ Chroma          │
│ DashScopeEmbed  │   │ Retriever       │
└────────────────┘   └────────────────┘
           │               │
           ▼               ▼
┌──────────────────────────────────────┐
│                Data 层                │
│ MySQL：文档信息 / 问答历史 / 用户     │
│ Chroma：chunk 向量                    │
│ Local File：原始 PDF                  │
│ Redis：后续 session / 缓存            │
└──────────────────────────────────────┘
```

---

# 4. 推荐目录结构

你后续可以按这个结构组织：

```text
remote_sense_rag/
│
├── backend/
│   └── app/
│       ├── main.py
│       │
│       ├── api/
│       │   ├── rag.py
│       │   ├── documents.py
│       │   ├── chat.py
│       │   └── users.py              # 后续加
│       │
│       ├── schemas/
│       │   ├── rag.py
│       │   ├── document.py
│       │   ├── chat.py
│       │   └── user.py               # 后续加
│       │
│       ├── services/
│       │   ├── rag_service.py
│       │   ├── vector_store_service.py
│       │   ├── document_service.py
│       │   └── chat_service.py
│       │
│       ├── model/
│       │   └── factory.py
│       │
│       ├── db/
│       │   ├── session.py            # MySQL 连接
│       │   └── models.py             # ORM 表结构
│       │
│       ├── core/
│       │   └── config.py
│       │
│       └── utils/
│           ├── file_handler.py
│           ├── logger_handler.py
│           ├── config_handler.py
│           └── prompt_loader.py
│
├── frontend/
│   └── streamlit_app.py
│
├── config/
│   ├── rag.yml
│   ├── chroma.yml
│   └── prompts.yml
│
├── prompts/
│   └── rag_summarize.txt
│
├── data/
│   └── uploads/
│
├── chroma_db/
├── logs/
├── docs/
├── requirements.txt
├── README.md
└── .env
```

---

# 5. 分层设计思想

## 5.1 前端层

前端只负责：

```text
展示页面
接收用户输入
上传文件
调用后端接口
展示后端结果
```

前端不负责：

```text
解析 PDF
embedding
向量检索
Prompt 构建
大模型调用
数据库复杂操作
```

当前使用 Streamlit 是合理的，因为它适合快速做 AI Demo。

后续如果你想更像正式产品，可以换成：

```text
Vue
React
Next.js
```

但不是当前优先级。

---

## 5.2 API 层

API 层负责：

```text
接收 HTTP 请求
参数校验
调用 Service
返回响应
```

例如：

```text
POST /api/rag/upload
POST /api/rag/ask
GET  /api/rag/stats
DELETE /api/rag/clear
```

API 层不应该写复杂业务逻辑。

错误示例：

```text
在 upload 接口里直接写 PDF 解析、切分、embedding、Chroma 入库。
```

推荐做法：

```text
upload 接口只负责保存文件，然后调用 rag_service.ingest_pdf()
```

---

## 5.3 Schema 层

Schema 层负责定义数据结构：

```text
前端请求后端的数据格式
后端返回前端的数据格式
```

例如：

```python
class AskRequest(BaseModel):
    question: str
    top_k: int = 4
```

好处：

```text
1. 自动校验参数
2. 自动生成接口文档
3. 前后端字段清晰
4. 后期维护方便
```

---

## 5.4 Service 层

Service 层负责业务逻辑。

例如：

```text
RAGService：
完整 RAG 问答流程

VectorStoreService：
Chroma 入库和检索

DocumentService：
文档元信息管理

ChatService：
问答历史管理
```

Service 层是后端项目的核心。

---

## 5.5 Model Factory 层

Factory 层负责创建模型对象：

```text
ChatTongyi
DashScopeEmbeddings
```

为什么要有 Factory？

因为后面你可能换模型：

```text
qwen-plus → qwen-max
DashScopeEmbeddings → bge-m3
百炼 → 其他兼容平台
```

如果模型创建代码散落在项目各处，后期很难改。

---

## 5.6 Data 层

Data 层包括：

```text
本地上传文件
Chroma 向量库
MySQL 业务数据库
Redis 缓存或 session
```

当前 demo 可以只有：

```text
data/uploads/
chroma_db/
```

但简历项目最好加：

```text
MySQL
```

---

# 6. 功能版本规划

## V1：基础 RAG 闭环版

目标：

```text
先跑通完整 RAG 主链路。
```

功能：

```text
1. 后端健康检查
2. PDF 上传
3. PDF 保存
4. PDF 解析
5. 文本切分
6. embedding 向量化
7. Chroma 入库
8. 知识库状态查看
9. 用户提问
10. Chroma 检索
11. Prompt 构建
12. 大模型回答
13. 来源片段展示
14. 清空知识库
```

这是当前最小可用版。

---

## V2：简历可写版

目标：

```text
从 demo 变成项目。
```

新增：

```text
1. 文档列表
2. 文档元信息保存
3. 问答历史保存
4. 删除指定文档
5. 多文档知识库
6. 按文档过滤检索
7. 页面整理
8. README + 架构图 + 截图
```

建议加入：

```text
MySQL
SQLAlchemy
```

---

## V3：工程化增强版

目标：

```text
体现后端工程能力。
```

新增：

```text
1. 用户登录
2. JWT 鉴权
3. 用户隔离知识库
4. 多轮对话 session
5. Redis 保存会话状态
6. 文件大小限制
7. 文件格式强校验
8. 日志记录
9. 统一异常处理
10. Docker Compose 一键启动
```

---

## V4：遥感领域助手版

目标：

```text
体现遥感领域特色。
```

新增：

```text
1. 遥感考研复习模式
2. 论文总结模式
3. 真题解析模式
4. 知识点提取模式
5. 自动生成复习提纲
6. OCR 支持扫描版 PDF
7. 支持 docx / txt / md
8. 知识库分组：教材 / 论文 / 真题 / 笔记
9. 导出问答记录
```

---

# 7. 核心功能怎么实现

## 7.1 PDF 上传

### 功能目标

用户在前端上传 PDF，后端保存文件。

### 前端

```python
uploaded_file = st.file_uploader("选择 PDF 文件", type=["pdf"])
```

点击上传：

```python
requests.post("/api/rag/upload", files=files)
```

### 后端

```python
@router.post("/upload")
async def upload_pdf(file: UploadFile):
    ...
```

保存文件：

```python
shutil.copyfileobj(file.file, f)
```

### 推荐增强

后续加：

```text
后缀名校验
MIME 类型校验
文件头校验
文件大小限制
MD5 去重
文件名重命名
```

---

## 7.2 文档解析

### 功能目标

把 PDF 转成 LangChain Document。

### 实现

```python
PyPDFLoader
```

输出：

```text
List[Document]
```

每个 Document：

```text
page_content：正文
metadata：source、page、doc_name
```

### 后续扩展

```text
TextLoader
DocxLoader
UnstructuredFileLoader
OCR Loader
```

---

## 7.3 文本切分

### 功能目标

把长文档切成 chunks。

### 实现

```python
RecursiveCharacterTextSplitter
```

推荐配置：

```python
chunk_size = 700
chunk_overlap = 100
separators = [
    "\\n\\n",
    "\\n",
    "。",
    "！",
    "？",
    "；",
    "，",
    " ",
    "",
]
```

### 调参思路

```text
chunk 太大：检索不精准，Prompt 太长
chunk 太小：上下文不足，回答碎片化
overlap：避免信息被切断
```

---

## 7.4 向量化

### 功能目标

把 chunk 文本转成向量。

### 实现

```python
DashScopeEmbeddings
```

模型：

```text
text-embedding-v3
```

### 作用

```text
文本 → 向量 → 相似度检索
```

这是 RAG 的核心基础。

---

## 7.5 Chroma 入库

### 功能目标

把 chunks 存入向量库。

### 实现

```python
Chroma.add_documents(chunks)
```

内部会：

```text
读取 page_content
调用 embedding_function
生成向量
保存向量
保存文本
保存 metadata
```

### 后续增强

```text
删除指定文档对应 chunks
避免重复入库
按用户隔离 collection
按文档类型分 collection
```

---

## 7.6 用户提问与检索

### 功能目标

用户提问时，从 Chroma 找到相关资料。

### 实现

```python
similarity_search_with_score(query, k=top_k)
```

返回：

```text
Document + score
```

### 后续增强

```text
score 阈值过滤
按文档过滤
按知识库过滤
rerank 重排
```

---

## 7.7 Prompt 构建

### 功能目标

把用户问题和检索资料拼成 Prompt。

### 实现

```python
PromptTemplate
```

Prompt 包含：

```text
角色设定
回答要求
检索资料
用户问题
输出格式
```

推荐要求：

```text
只根据资料回答
资料不足就说明
不要编造
适合考研复习
结尾列出参考来源
```

---

## 7.8 大模型回答

### 功能目标

调用百炼模型生成答案。

### 实现

```python
ChatTongyi
```

链式写法：

```python
chain = prompt | model | StrOutputParser()
```

### 后续增强

不同模式使用不同 Prompt：

```text
普通问答
考研复习
论文总结
真题解析
知识点提取
```

---

## 7.9 来源片段展示

### 功能目标

让回答可追溯。

### 返回字段

```json
{
  "answer": "...",
  "sources": [
    {
      "doc_name": "遥感导论.pdf",
      "page": 12,
      "score": 0.32,
      "text": "..."
    }
  ]
}
```

### 前端展示

```python
st.expander()
```

显示：

```text
文档名
页码
score
片段内容
```

这个功能非常重要，因为 RAG 项目要体现：

```text
可信来源
可追溯
防止幻觉
```

---

## 7.10 文档管理

### 功能目标

让用户知道自己上传了哪些文档。

### V2 实现

加入 MySQL documents 表：

```text
id
filename
file_path
file_md5
file_size
chunk_count
status
created_at
updated_at
```

### 接口

```text
GET    /api/documents
DELETE /api/documents/{document_id}
```

### 注意

删除文档时，应该同时删除：

```text
MySQL 文档记录
本地 PDF 文件
Chroma 中对应 chunks
```

---

## 7.11 问答历史

### 功能目标

保存用户问过什么，模型答了什么。

### MySQL 表

chat_sessions：

```text
id
title
created_at
updated_at
```

chat_messages：

```text
id
session_id
role
content
sources_json
created_at
```

### 接口

```text
GET  /api/chats
GET  /api/chats/{session_id}
POST /api/rag/ask
```

其中 `/ask` 在返回答案的同时，把问答写入数据库。

---

# 8. 推荐数据库设计

## 8.1 documents 表

```text
id              主键
filename        原始文件名
file_path       文件保存路径
file_md5        文件 MD5
file_size       文件大小
chunk_count     切分数量
status          uploaded / indexed / failed
created_at      创建时间
updated_at      更新时间
```

---

## 8.2 chat_sessions 表

```text
id
title
created_at
updated_at
```

---

## 8.3 chat_messages 表

```text
id
session_id
role            user / assistant
content
sources_json
created_at
```

---

# 9. 推荐开发顺序

## 阶段 1：稳定当前 RAG 主链路

时间：

```text
2～3 天
```

任务：

```text
跑通上传
跑通入库
跑通提问
跑通来源展示
调整 Prompt
整理 README
```

目标：

```text
能完整演示。
```

---

## 阶段 2：加入文档管理

时间：

```text
5～7 天
```

任务：

```text
加 MySQL
建 documents 表
保存文档记录
显示文档列表
防止重复上传
删除指定文档
```

目标：

```text
从 demo 变成项目。
```

---

## 阶段 3：加入问答历史

时间：

```text
3～5 天
```

任务：

```text
建 chat_sessions 表
建 chat_messages 表
保存用户问题
保存模型回答
保存 sources
前端展示历史记录
```

目标：

```text
体现后端业务能力。
```

---

## 阶段 4：优化 RAG 效果

时间：

```text
3～5 天
```

任务：

```text
调 chunk_size
调 top_k
加 score 阈值
优化 Prompt
增加不同模式
```

目标：

```text
回答更稳定。
```

---

## 阶段 5：工程化包装

时间：

```text
3～5 天
```

任务：

```text
Dockerfile
docker-compose
项目截图
架构图
接口文档
README
简历描述
```

目标：

```text
可以放 GitHub 和简历。
```

---

# 10. 最小可投递版本

你最少做到：

```text
FastAPI 后端
Streamlit 前端
LangChain RAG
Chroma 向量库
DashScopeEmbeddings
ChatTongyi
PDF 上传
知识库构建
智能问答
来源片段展示
文档列表
问答历史
README + 架构图
```

如果再加：

```text
MySQL
Docker
```

项目质量会明显更像实习项目。

---

# 11. 简历描述参考

项目名称：

```text
遥感领域知识库智能问答系统
```

技术栈：

```text
FastAPI、Streamlit、LangChain、Chroma、DashScope、MySQL、SQLAlchemy
```

简历描述：

```text
基于 FastAPI、LangChain、Chroma 和百炼大模型构建遥感领域知识库问答系统，支持 PDF 资料上传、文本解析、递归切分、向量化入库、相似度检索和基于检索增强生成的智能问答。
```

项目要点：

```text
1. 使用 FastAPI 设计文档上传、知识库状态、智能问答、历史记录等 RESTful API；
2. 基于 PyPDFLoader 和 RecursiveCharacterTextSplitter 实现 PDF 文档解析与 chunk 切分；
3. 使用 DashScopeEmbeddings 生成文本向量，并基于 Chroma 构建本地持久化向量库；
4. 结合 PromptTemplate、ChatTongyi 和 StrOutputParser 构建 RAG 问答链，实现基于资料来源的回答生成；
5. 使用 MySQL 保存文档元信息和问答历史，支持文档管理与历史追踪；
6. 使用 Streamlit 构建交互页面，支持文件上传、知识库状态查看、问答结果展示和来源片段追溯。
```

---

# 12. 当前阶段不要做什么

暂时不要优先做：

```text
复杂 Agent
多智能体
React/Vue 大前端
微服务
复杂权限系统
云服务器部署
复杂工作流编排
```

你当前最应该做：

```text
FastAPI + LangChain + Chroma + MySQL 主线跑通
```

---

# 13. 总结

这个项目的核心设计思想是：

```text
前端只负责交互；
FastAPI 只负责接口；
Schema 负责数据格式；
Service 负责业务流程；
Factory 负责模型创建；
VectorStore 负责向量检索；
Chroma 负责语义检索；
MySQL 负责业务数据；
LLM 负责基于资料生成回答。
```

你的路线：

```text
先完成 RAG 主链路
↓
加文档管理
↓
加问答历史
↓
加 MySQL
↓
优化 Prompt 和检索
↓
Docker + README + 简历包装
```

你真正要训练的能力不是背 API，而是：

```text
知道一个功能应该放在哪一层；
知道前端传什么；
知道后端接什么；
知道业务逻辑怎么组织；
知道数据怎么保存；
知道以后怎么扩展。
```

等你能把这套架构讲清楚，就已经不是只会跑 demo，而是具备了初步 AI 应用后端项目能力。
