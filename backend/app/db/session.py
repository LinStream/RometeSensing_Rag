"""
数据库连接配置。

使用 SQLAlchemy 异步连接 MySQL。
所有敏感配置通过环境变量注入，不硬编码。
"""

import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required. "
        "Example: mysql+aiomysql://user:pass@localhost:3306/remote_rag?charset=utf8mb4"
    )


class Base(DeclarativeBase):
    """
    所有 ORM 模型的统一基类。
    """
    pass


_engine_kwargs = {
    "echo": os.environ.get("SQL_ECHO", "false").lower() == "true",
}

# SQLite 不支持连接池参数，仅对 MySQL 等生产数据库设置
if not DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(pool_size=10, max_overflow=20)

async_engine = create_async_engine(DATABASE_URL, **_engine_kwargs)


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    FastAPI 数据库依赖。

    每次请求：
    1. 创建数据库 session
    2. yield 给接口使用
    3. 请求结束后关闭
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()