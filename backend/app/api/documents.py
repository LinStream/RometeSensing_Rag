import logging
import os

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.crud.document import list_documents, delete_document_by_id, get_document_by_id
from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.document import DocumentResponse
from backend.app.services.runtime import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def get_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await list_documents(db, page=page, page_size=page_size)

    return PaginatedResponse(
        items=rows,
        total=total,
        page=page,
        page_size=page_size,
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    删除指定文档。

    删除顺序：
    1. 查 MySQL，确认文档存在并拿到 file_path
    2. 删除 Chroma 中 document_id 对应的 chunks
    3. 删除本地上传文件
    4. 删除 MySQL documents 记录

    这样可以尽量保证 MySQL、本地文件、Chroma 三者一致。
    """
    document = await get_document_by_id(db, document_id=document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 1. 删除 Chroma 向量数据，同时清理 md5 记录
    try:
        rag_service.delete_document(
            document_id=document_id,
            file_path=document.file_path,
        )
    except (OSError, RuntimeError) as e:
        logger.exception("删除 Chroma 向量数据失败: document_id=%s", document_id)
        raise HTTPException(
            status_code=500,
            detail="删除向量数据失败，请检查服务端日志。",
        )

    # 2. 删除本地文件。文件不存在时不报错，因为可能已经被手动删除。
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except OSError as e:
            logger.exception("删除本地文件失败: %s", document.file_path)
            raise HTTPException(
                status_code=500,
                detail="删除本地文件失败，请检查服务端日志。",
            )

    # 3. 最后删除 MySQL 记录
    await delete_document_by_id(db, document_id=document_id)

    return {
        "message": "文档删除成功",
        "document_id": document_id,
    }
