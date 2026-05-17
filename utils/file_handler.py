"""
文件处理工具，尽量沿用参考项目的写法。

包括：
1. 计算文件 MD5，用于防止重复入库；
2. 列出允许类型的知识库文件；
3. 使用 LangChain Loader 加载 PDF / TXT。
"""

import hashlib
import os
from typing import Iterable

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from utils.logger_handler import logger


def get_file_md5_hex(filepath: str):
    """
    获取文件 md5 十六进制字符串。
    用于判断文件是否已经入库过。
    """
    if not os.path.exists(filepath):
        logger.error(f"[md5计算] 文件 {filepath} 不存在")
        return None

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算] 路径 {filepath} 不是文件")
        return None

    md5_obj = hashlib.md5()
    chunk_size = 4096

    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"[md5计算] 计算文件 {filepath} md5 失败：{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str, ...]) -> tuple[str, ...]:
    """
    返回文件夹中允许后缀的文件路径。
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] {path} 不是文件夹")
        return tuple(files)

    for f in os.listdir(path):
        if f.lower().endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    """
    使用 LangChain PyPDFLoader 加载 PDF。
    """
    docs = PyPDFLoader(filepath, passwd).load()
    for doc in docs:
        doc.metadata["doc_name"] = os.path.basename(filepath)
    return docs


def txt_loader(filepath: str) -> list[Document]:
    """
    使用 LangChain TextLoader 加载 TXT。
    """
    docs = TextLoader(filepath, encoding="utf-8").load()
    for doc in docs:
        doc.metadata["doc_name"] = os.path.basename(filepath)
    return docs
