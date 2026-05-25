"""
Reranker 重排模块。

核心原理：
- 向量检索用的是 bi-encoder（query 和 doc 分别编码为向量，再算余弦相似度）
  → 速度快，但无法捕捉 query 和 doc 之间的细粒度交互
- Reranker 用的是 cross-encoder（query 和 doc 拼接后一起编码）
  → 速度慢，但能捕捉 token 级别的相关性，精度更高

工业界标准做法：先用 bi-encoder 粗筛 top-N（比如 20），再用 cross-encoder 精排取 top-K（比如 3-5）。
本项目用 DashScope 的 gte-rerank 模型作为 reranker，与现有 LLM/Embedding 同一服务商，不需要额外注册。
"""

import logging

from dashscope import TextReRank

logger = logging.getLogger(__name__)


class DashScopeReranker:
    """
    基于 DashScope gte-rerank 模型的 Reranker。

    API 调用方式：dashscope.TextReRank.call()
    输入：query + documents 列表
    输出：按相关性重排后的 documents 列表，附带 relevance_score
    """

    def __init__(self, model: str = "gte-rerank-v2", top_n: int = 5):
        self.model = model
        self.top_n = top_n

    def rerank(self, query: str, documents: list[str], top_n: int | None = None):
        """
        对文档列表按与 query 的相关性重排。

        参数：
        - query: 用户问题
        - documents: 待重排的文档内容列表（字符串列表）
        - top_n: 返回 top_n 个结果，None 则用 self.top_n

        返回：list[dict]，每项包含 {"index": 原始索引, "relevance_score": 分数}
              按 relevance_score 降序排列
        """
        if not documents:
            return []

        n = top_n or self.top_n

        try:
            response = TextReRank.call(
                model=self.model,
                query=query,
                documents=documents,
                top_n=min(n, len(documents)),
            )

            if response.status_code != 200:
                logger.error("Rerank API 调用失败: %s", response.message)
                return [
                    {"index": i, "relevance_score": 0.0}
                    for i in range(min(n, len(documents)))
                ]

            results = response.output.results
            return [
                {"index": r.index, "relevance_score": r.relevance_score}
                for r in results
            ]

        except Exception:
            logger.exception("Rerank 调用异常")
            return [
                {"index": i, "relevance_score": 0.0}
                for i in range(min(n, len(documents)))
            ]
