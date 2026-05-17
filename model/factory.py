"""
模型工厂。

严格参考你给的项目：
- ChatTongyi 作为聊天模型
- DashScopeEmbeddings 作为 embedding 模型

为了方便你当前环境，如果没有 DASHSCOPE_API_KEY，
会尝试用 OPENAI_API_KEY 兼容设置。
"""

import os
from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

from utils.config_handler import rag_conf


def ensure_dashscope_api_key():
    """
    ChatTongyi / DashScopeEmbeddings 默认读取 DASHSCOPE_API_KEY。
    如果用户只配置了 OPENAI_API_KEY，这里自动复制过去，降低配置成本。
    """
    if not os.getenv("DASHSCOPE_API_KEY") and os.getenv("OPENAI_API_KEY"):
        os.environ["DASHSCOPE_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        ensure_dashscope_api_key()
        return ChatTongyi(model=rag_conf["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        ensure_dashscope_api_key()
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
