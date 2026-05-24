"""
知识库管理相关请求/响应模型。
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_count: int
    document_id: int | None = None


class StatsResponse(BaseModel):
    collection_name: str
    chunks_count: int
