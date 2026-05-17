# 接口文档：参考 agent.zip 结构版 RAG 项目

## 1. 接口总览

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/health` | 测试后端连接 |
| POST | `/api/rag/upload` | 上传 PDF/TXT 并入库 |
| POST | `/api/rag/ask` | 向知识库提问 |
| GET | `/api/rag/stats` | 查看知识库状态 |
| POST | `/api/rag/load-all` | 批量加载 data 目录 |
| DELETE | `/api/rag/clear` | 清空知识库 |

## 2. GET /health

响应：

```json
{
  "status": "ok"
}
```

## 3. POST /api/rag/upload

请求类型：

```text
multipart/form-data
```

前端示例：

```python
files = {
    "file": (
        uploaded_file.name,
        uploaded_file.getvalue(),
        uploaded_file.type or "application/octet-stream",
    )
}

resp = requests.post(
    f"{API_BASE_URL}/api/rag/upload",
    files=files,
)
```

响应示例：

```json
{
  "message": "文件上传并入库成功",
  "filename": "遥感导论.pdf",
  "chunks_count": 36
}
```

调用链：

```text
upload_file()
↓
rag_service.load_single_file()
↓
VectorStoreService.load_single_file()
↓
pdf_loader / txt_loader
↓
splitter.split_documents()
↓
vector_store.add_documents()
```

## 4. POST /api/rag/ask

请求 JSON：

```json
{
  "question": "什么是遥感？",
  "top_k": 4
}
```

响应 JSON：

```json
{
  "answer": "遥感是指……",
  "sources": [
    {
      "doc_name": "遥感导论.pdf",
      "page": 1,
      "text": "……",
      "metadata": {}
    }
  ]
}
```

调用链：

```text
ask()
↓
rag_service.rag_summarize_with_sources()
↓
retriever_docs()
↓
_format_context()
↓
PromptTemplate
↓
ChatTongyi
↓
StrOutputParser
```

## 5. GET /api/rag/stats

响应：

```json
{
  "collection_name": "remote_sensing_rag",
  "chunks_count": 128
}
```

## 6. POST /api/rag/load-all

作用：加载 `config/chroma.yml` 中 `data_path` 指定目录下所有允许类型的文件。

响应：

```json
{
  "message": "批量加载完成",
  "chunks_count": 128
}
```

## 7. DELETE /api/rag/clear

响应：

```json
{
  "message": "知识库已清空"
}
```
