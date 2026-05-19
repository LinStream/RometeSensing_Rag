# RemoteSense-Agent：基于 LangChain Agent 的遥感资料智能问答系统

## 1. 项目简介

RemoteSense-Agent 是一个面向遥感学习与资料问答场景的智能问答系统。系统支持用户上传 PDF / TXT 格式的遥感教材、真题、论文或复习资料，并将资料构建为本地向量知识库。用户在前端输入问题后，后端通过 LangChain Agent 统一接收问题，并在需要时调用 RAG 工具完成知识库检索与回答生成。

本项目不是简单的大模型 API 调用，而是一个包含 **Agent 工具调用、RAG 知识库、文档管理、MySQL 持久化、Chroma 向量检索、FastAPI 后端接口和 Streamlit 前端展示** 的完整 AI 应用项目。

项目定位：

```text
一个以 LangChain Agent 为主入口，将 RAG 知识库问答封装为工具的遥感资料智能问答系统。
```

---

## 2. 项目背景

在遥感学习和考研复习过程中，常见资料包括遥感教材、课程讲义、真题、论文和个人笔记。这些资料内容多、篇幅长，传统检索方式效率较低。为了提升资料查询和知识复习效率，本项目尝试构建一个遥感领域的智能问答系统。

系统将上传的文档切分为文本块，并通过 DashScope Embeddings 转换为向量后存入 Chroma 向量数据库。用户提问时，LangChain Agent 会根据问题判断是否调用 RAG 工具。如果问题属于遥感资料问答场景，Agent 会调用 RAG 工具完成知识库检索，并结合大模型生成回答。

---

## 3. 技术栈

| 模块 | 技术 |
|---|---|
| 前端 | Streamlit |
| 后端 | FastAPI |
| Agent 框架 | LangChain `create_agent` |
| 大模型 | 阿里百炼 / DashScope ChatTongyi |
| Embedding | DashScopeEmbeddings |
| 向量数据库 | Chroma |
| 关系型数据库 | MySQL |
| ORM | SQLAlchemy AsyncSession |
| 文档解析 | PyPDFLoader / TextLoader |
| 文本切分 | RecursiveCharacterTextSplitter |
| 接口请求 | requests |
| 配置管理 | YAML 配置文件 |

---

## 4. 核心功能

### 4.1 文档上传与知识库入库

系统支持上传：

```text
PDF
TXT
```

上传后会执行：

```text
保存文件
↓
计算文件 MD5
↓
检查是否重复上传
↓
创建 MySQL 文档记录
↓
解析文档内容
↓
切分文本 chunk
↓
调用 Embedding 模型生成向量
↓
写入 Chroma 向量数据库
↓
更新文档状态 indexed / failed
```

### 4.2 基于 MD5 的重复上传检测

系统会对上传文件计算 MD5 值，并在 MySQL 的 `documents` 表中保存 `file_md5` 字段。

如果检测到已经存在：

```text
相同 file_md5
且 status = indexed
```

则认为该文件已经成功入库，系统会拒绝重复上传，避免：

```text
MySQL 文档记录重复
Chroma 向量数据重复
Embedding 重复调用
检索结果重复命中
```

### 4.3 文档管理

系统支持：

```text
查看已上传文档
删除指定文档
查看文档入库状态
```

删除文档时会同步清理：

```text
MySQL documents 表记录
本地上传文件
Chroma 中该文档对应的 chunks
MD5 相关记录
```

### 4.4 Agent 智能问答

用户提问时，前端统一调用：

```text
POST /api/chat/ask
```

后端不再让前端直接选择 RAG 或其他能力，而是统一交给 LangChain Agent。

Agent 会根据用户问题和工具描述，判断是否调用工具。目前主要工具包括：

```text
rag_summarize：遥感知识库问答工具
chat_direct：普通问候和自我介绍工具
```

### 4.5 RAG 作为 Agent Tool

本项目将原有 RAG 能力封装为 LangChain Tool：

```text
Agent
↓
rag_summarize tool
↓
RagSummarizeService
↓
Chroma 检索
↓
Prompt 构造
↓
ChatTongyi 生成回答
```

也就是说，RAG 不再直接作为唯一问答入口，而是成为 Agent 可以调用的一个工具。

### 4.6 多轮对话与历史记录

系统使用 MySQL 保存：

```text
chat_sessions
chat_messages
```

用户每次提问时，后端会根据 `session_id` 获取当前会话，并保存本轮问答记录。系统支持会话历史查询，为后续多轮对话和上下文增强提供基础。

### 4.7 Streamlit 聊天式前端

前端采用 Streamlit 实现，支持：

```text
聊天式输入
聊天历史展示
文档上传
文档列表展示
文档删除
伪流式输出
```

回答展示使用 `st.chat_message()` 和 `st.write_stream()` 实现类似流式输出的效果。

---

## 5. 项目架构

### 5.1 总体架构

```text
                         Streamlit 前端
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
   文档管理操作                                  用户提问
        │                                           │
 /api/rag/upload                              /api/chat/ask
 /api/documents                                    │
        │                                           │
        ↓                                           ↓
   FastAPI 文档接口                           FastAPI 聊天接口
        │                                           │
        ↓                                           ↓
   Document / RAG 流程                      LangChain Agent
        │                                           │
        ↓                                           ↓
 本地文件 + MySQL + Chroma              调用 rag_summarize Tool
                                                    │
                                                    ↓
                                             RagSummarizeService
                                                    │
                                                    ↓
                                               Chroma 检索
                                                    │
                                                    ↓
                                               ChatTongyi 回答
                                                    │
                                                    ↓
                                             MySQL 保存问答历史
```

### 5.2 目录结构

```text
project/
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── chat.py          # 统一聊天问答接口
│       │   ├── rag.py           # 知识库上传、状态、清空等接口
│       │   ├── documents.py     # 文档列表与删除接口
│       │   └── chats.py         # 会话历史接口
│       ├── crud/
│       │   ├── document.py      # 文档表增删改查
│       │   └── chat.py          # 会话与消息增删改查
│       ├── db/
│       │   ├── models.py        # ORM 表模型
│       │   └── session.py       # MySQL 异步连接
│       ├── schemas/
│       │   ├── chat.py          # 聊天接口请求响应模型
│       │   ├── document.py      # 文档接口响应模型
│       │   └── rag.py           # RAG 上传接口响应模型
│       └── services/
│           └── runtime.py       # 运行时服务对象统一创建
│
├── agent/
│   ├── react_agent.py           # LangChain create_agent 创建
│   ├── tools.py                 # Agent tools 定义
│   └── tool_context.py          # 工具执行临时上下文
│
├── rag/
│   ├── rag_service.py           # RAG 检索与回答逻辑
│   └── vector_store.py          # Chroma 入库、检索、删除
│
├── model/
│   └── factory.py               # ChatTongyi 和 Embedding 模型工厂
│
├── utils/
│   ├── config_handler.py        # YAML 配置读取
│   ├── file_handler.py          # 文件 MD5 等工具
│   ├── path_tool.py             # 路径处理
│   └── prompt_loader.py         # Prompt 加载
│
├── frontend/
│   └── streamlit_app.py         # Streamlit 前端页面
│
├── config/
│   ├── rag.yml                  # 模型配置
│   ├── chroma.yml               # Chroma 与切分配置
│   └── prompts.yml              # Prompt 文件配置
│
├── prompts/
│   ├── agent_system_prompt.txt  # Agent 系统提示词
│   └── rag_summarize.txt        # RAG 问答提示词
│
└── docs/
```

---

## 6. 核心流程说明

### 6.1 文档上传入库流程

```text
用户上传 PDF / TXT
↓
Streamlit 调用 /api/rag/upload
↓
FastAPI 保存文件到 data 目录
↓
计算文件 MD5
↓
查询 MySQL 是否已有相同 file_md5 且 status=indexed 的文档
↓
如果重复：返回 409，拒绝重复上传
↓
如果不重复：创建 documents 记录，status=uploaded
↓
调用 RagSummarizeService.load_single_file()
↓
VectorStoreService 加载文件、切分文本、写入 Chroma
↓
成功：更新 documents.status=indexed，记录 chunk_count
↓
失败：更新 documents.status=failed，记录 error_message
```

### 6.2 Agent 问答流程

```text
用户输入问题
↓
Streamlit 调用 /api/chat/ask
↓
FastAPI 获取或创建 chat_session
↓
查询当前 session 最近历史消息
↓
调用 ReactAgent.invoke()
↓
LangChain create_agent 接收用户问题、历史对话和工具列表
↓
Agent 判断是否调用工具
↓
如果是遥感资料问题，调用 rag_summarize tool
↓
rag_summarize 调用 RagSummarizeService.rag_summarize_with_sources()
↓
Chroma 检索相关 chunks
↓
构造 RAG Prompt
↓
调用 ChatTongyi 生成回答
↓
工具结果返回 Agent
↓
Agent 返回最终回答
↓
FastAPI 保存 question、answer、sources 到 chat_messages
↓
返回前端
↓
Streamlit 使用 write_stream 伪流式展示
```

---

## 7. 数据库设计

### 7.1 documents 表

用于保存上传文档信息。

| 字段 | 说明 |
|---|---|
| id | 文档 ID |
| filename | 原始文件名 |
| file_path | 本地文件路径 |
| file_type | 文件类型 |
| file_md5 | 文件 MD5，用于重复上传检测 |
| chunk_count | 切分后的文本块数量 |
| status | 文档状态：uploaded / indexed / failed |
| error_message | 入库失败时的错误信息 |
| created_at | 创建时间 |
| updated_at | 更新时间 |

其中 `status` 的含义：

```text
uploaded：文件已保存，但尚未成功写入 Chroma
indexed：文件已成功切分、向量化并写入 Chroma，可用于检索
failed：文件入库失败，错误信息保存在 error_message
```

### 7.2 chat_sessions 表

用于保存会话信息。

| 字段 | 说明 |
|---|---|
| id | 会话 ID |
| session_name | 会话名称 |
| created_at | 创建时间 |
| updated_at | 更新时间 |

### 7.3 chat_messages 表

用于保存问答历史。

| 字段 | 说明 |
|---|---|
| id | 消息 ID |
| session_id | 所属会话 ID |
| question | 用户问题 |
| answer | 模型回答 |
| sources_json | 引用来源信息 |
| created_at | 创建时间 |

---

## 8. 接口说明

### 8.1 智能问答接口

```http
POST /api/chat/ask
```

请求示例：

```json
{
  "question": "什么是遥感？",
  "session_id": null
}
```

响应示例：

```json
{
  "answer": "遥感是指在不直接接触目标物的情况下...",
  "sources": [],
  "session_id": 1,
  "tool": "rag_summarize",
  "agent_type": "langchain_create_agent"
}
```

### 8.2 上传文档接口

```http
POST /api/rag/upload
```

请求类型：

```text
multipart/form-data
```

字段：

```text
file
```

响应示例：

```json
{
  "message": "文件上传并入库成功",
  "filename": "遥感导论.pdf",
  "chunks_count": 128,
  "document_id": 1
}
```

### 8.3 查看文档列表

```http
GET /api/documents
```

### 8.4 删除文档

```http
DELETE /api/documents/{document_id}
```

删除时会同步清理：

```text
MySQL 文档记录
本地文件
Chroma 向量数据
```

### 8.5 查看知识库状态

```http
GET /api/rag/stats
```

### 8.6 查看会话列表

```http
GET /api/chats
```

### 8.7 查看会话消息

```http
GET /api/chats/{session_id}/messages
```

---

## 9. 运行方式

### 9.1 安装依赖

```bash
pip install -r requirements.txt
```

### 9.2 配置环境变量

需要配置百炼 API Key。

可以在系统环境变量中配置：

```bash
DASHSCOPE_API_KEY=你的百炼APIKey
```

或在 `.env` 文件中配置，具体根据项目当前配置读取方式调整。

### 9.3 创建 MySQL 数据库

```sql
CREATE DATABASE remote_rag DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

数据库连接配置位于：

```text
backend/app/db/session.py
```

### 9.4 启动后端

```bash
uvicorn backend.app.main:app --reload --port 8000
```

FastAPI 文档地址：

```text
http://127.0.0.1:8000/docs
```

### 9.5 启动前端

```bash
streamlit run frontend/streamlit_app.py
```

---

## 10. 配置说明

### 10.1 模型配置

文件：

```text
config/rag.yml
```

示例：

```yaml
chat_model_name: qwen-plus
embedding_model_name: text-embedding-v4
```

### 10.2 Chroma 配置

文件：

```text
config/chroma.yml
```

常见配置：

```yaml
collection_name: remote_sensing_rag
persist_directory: chroma_db
k: 4
data_path: data
chunk_size: 700
chunk_overlap: 100
allow_knowledge_file_type:
  - pdf
  - txt
```

说明：

```text
k：检索返回的相关文本块数量
chunk_size：文本切分长度
chunk_overlap：文本块重叠长度
```

---

## 11. 项目亮点

### 11.1 LangChain Agent + RAG Tool

项目不是直接让前端调用 RAG，而是通过 LangChain `create_agent` 构建 Agent，将 RAG 能力封装为 `rag_summarize` 工具。用户提问后，由 Agent 根据问题自动决定是否调用知识库工具。

### 11.2 遥感领域知识库问答

项目结合用户遥感专业背景，面向遥感教材、真题、论文资料构建知识库，具有明确垂直领域场景。

### 11.3 MySQL + Chroma 双存储设计

系统使用 Chroma 负责向量相似度检索，使用 MySQL 保存文档元信息、文档状态、会话和问答历史，实现向量检索与业务管理分离。

### 11.4 文档生命周期管理

系统支持文档上传、MD5 去重、状态维护、入库失败记录、文档删除和向量数据清理，具备真实项目中文档管理的基本能力。

### 11.5 伪流式聊天体验

前端基于 `st.chat_message()` 和 `st.write_stream()` 实现聊天式交互和伪流式输出，使项目展示效果更接近真实智能问答产品。

---

## 12. 项目不足与后续优化

当前项目仍是初版 AI 应用项目，后续可以继续优化：

```text
1. 接入真正的后端流式输出：FastAPI StreamingResponse / SSE
2. 支持更多文档格式：docx、markdown、网页链接
3. 支持 OCR，处理扫描版 PDF
4. 增加 Dockerfile 和 docker-compose，实现一键部署
5. 增加用户登录和权限管理
6. 将文档服务进一步拆分为独立 DocumentService
7. 增加更多 Agent Tools，如文档列表查询、SQL 查询、联网搜索等
8. 优化 Agent 工具调用结果的结构化返回
9. 增加日志记录和异常追踪
10. 使用 Alembic 管理数据库迁移
```

---

## 13. 简历项目描述

可以在简历中这样描述：

```text
RemoteSense-Agent：基于 LangChain Agent 的遥感资料智能问答系统

- 基于 FastAPI 构建后端服务，设计文档上传、文档管理、智能问答和历史记录查询等接口；
- 使用 LangChain create_agent 构建工具调用式 Agent，将遥感知识库 RAG 能力封装为 Agent Tool，由 Agent 根据用户问题自动调用知识库工具完成回答；
- 使用 DashScopeEmbeddings 与 Chroma 构建向量知识库，实现 PDF/TXT 文档解析、文本切分、向量化入库和相似度检索；
- 使用 MySQL 持久化保存文档元信息、入库状态、会话信息和问答历史，支持文档状态追踪和问答记录管理；
- 基于文件 MD5 实现重复上传检测，并在文档删除时同步清理本地文件、MySQL 记录和 Chroma 向量数据；
- 使用 Streamlit 构建聊天式前端页面，支持资料上传、文档管理、Agent 问答和伪流式输出展示。
```

---

## 14. 面试讲解思路

如果面试官问“这个项目怎么运行”，可以按下面顺序讲：

```text
1. 用户先通过 Streamlit 上传 PDF 或 TXT 资料；
2. 后端 FastAPI 保存文件，并计算 MD5 判断是否重复上传；
3. 不重复时，在 MySQL documents 表中创建记录，并将文档切分、向量化后写入 Chroma；
4. 用户提问时，前端调用 /api/chat/ask；
5. 后端读取当前 session 的历史对话，并调用 LangChain Agent；
6. Agent 根据工具描述判断是否调用 rag_summarize 工具；
7. rag_summarize 工具内部调用 RAG 服务，从 Chroma 中检索相关资料并生成回答；
8. 后端将本轮问答保存到 MySQL，并把回答返回给前端；
9. 前端使用聊天式页面和伪流式方式展示回答。
```

如果面试官问“为什么要引入 Agent”，可以回答：

```text
原来的 RAG 问答是用户问题直接进入 RAG 服务，系统能力比较单一。引入 Agent 后，RAG 被封装成一个工具，后续可以继续扩展文档管理工具、SQL 查询工具、联网搜索工具等。Agent 作为统一入口，根据用户问题决定调用哪个工具，从而让系统从单一 RAG 问答扩展为工具调用式智能助手。
```

如果面试官问“MySQL 和 Chroma 分别负责什么”，可以回答：

```text
Chroma 负责向量存储和相似度检索，主要用于 RAG 问答；MySQL 负责业务数据管理，包括文档元信息、入库状态、会话信息和问答历史。两者分工不同，Chroma 解决语义检索问题，MySQL 解决业务记录和状态管理问题。
```

---

## 15. 项目总结

本项目从一个简单的 RAG demo 逐步扩展为一个包含 Agent 调度、RAG 知识库、文档管理、数据库持久化和前端交互的 AI 应用项目。当前版本已经具备作为实习简历项目的基本完整度，能够体现 FastAPI 后端开发、LangChain Agent 使用、RAG 检索增强生成、MySQL 数据管理和 Streamlit 前端交互等能力。
