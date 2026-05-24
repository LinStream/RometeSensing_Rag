"""
向量库服务。

这个文件尽量参考你提供的 agent 项目写法：
- Chroma
- RecursiveCharacterTextSplitter
- DashScopeEmbeddings（从 model.factory 中导入 embed_model）
- pdf_loader / txt_loader
- md5 去重
"""

import os
from typing import List

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import embed_model
from utils.config_handler import chroma_conf
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loader,
    txt_loader,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

        # 混合检索配置
        hybrid_conf = chroma_conf.get("hybrid_search", {})
        self.hybrid_enabled = hybrid_conf.get("enabled", False)
        self.bm25_top_k = hybrid_conf.get("bm25_top_k", 15)
        self.rrf_k = hybrid_conf.get("rrf_k", 60)
        self._bm25_retriever: BM25Retriever | None = None

    def get_retriever(self):
        """
        返回 retriever，供 RagSummarizeService 调用。
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def _md5_store_path(self) -> str:
        """
        md5.text 的绝对路径。
        """
        return get_abs_path(chroma_conf["md5_hex_store"])

    def _check_md5_hex(self, md5_for_check: str) -> bool:
        """
        检查某个文件 md5 是否已经处理过。
        True：处理过
        False：没处理过
        """
        md5_store_path = self._md5_store_path()

        if not os.path.exists(md5_store_path):
            open(md5_store_path, "w", encoding="utf-8").close()
            return False

        with open(md5_store_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.strip() == md5_for_check:
                    return True

        return False

    def _save_md5_hex(self, md5_for_save: str):
        """
        保存已处理文件的 md5。
        """
        with open(self._md5_store_path(), "a", encoding="utf-8") as f:
            f.write(md5_for_save + "\n")

    def _remove_md5_hex(self, md5_for_remove: str):
        """
        删除某个文件的 md5 记录。

        为什么删除文档时要同步删除 md5？
        因为当前项目用 md5.text 判断文件是否已经入库。
        如果只删除 Chroma 和本地文件，但 md5 还留着，
        后面重新上传同一个文件时会被误判为“已经入库”，从而跳过。
        """
        md5_store_path = self._md5_store_path()

        if not os.path.exists(md5_store_path):
            return

        with open(md5_store_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(md5_store_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.strip() != md5_for_remove:
                    f.write(line)

    def _get_file_documents(self, read_path: str) -> list[Document]:
        """
        根据文件类型调用不同 loader。
        """
        lower_path = read_path.lower()

        if lower_path.endswith(".txt"):
            return txt_loader(read_path)

        if lower_path.endswith(".pdf"):
            return pdf_loader(read_path)

        return []

    def _split_documents(self, documents: list[Document]) -> list[Document]:
        """
        文档切分，并过滤空 chunk。
        """
        split_documents = self.splitter.split_documents(documents)

        split_documents = [
            doc for doc in split_documents
            if isinstance(doc.page_content, str) and doc.page_content.strip()
        ]

        return split_documents

    def load_single_file(
        self,
        file_path: str,
        document_id: int | None = None,
        file_md5: str | None = None,
    ) -> int:
        """
        加载单个文件到向量库。

        参数：
        - file_path：本地文件路径
        - document_id：MySQL documents 表中的主键 id
        - file_md5：上传接口提前计算好的文件 MD5；如果没有传入，这里才自己计算。

        为什么要把 document_id 写进 Chroma metadata？
        因为删除指定文档时，需要根据 document_id 找到 Chroma 中属于该文档的所有 chunks。
        """
        md5_hex = file_md5 or get_file_md5_hex(file_path)

        if not md5_hex:
            raise ValueError(f"无法计算文件 md5：{file_path}")

        if self._check_md5_hex(md5_hex):
            logger.info(f"[加载知识库] {file_path} 内容已经存在知识库内，跳过")
            return 0

        documents = self._get_file_documents(file_path)

        if not documents:
            raise ValueError(f"{file_path} 没有有效文本内容，可能是扫描版 PDF 或空文件")

        # 给每个原始 Document 补充 document_id。
        # splitter 切分后，metadata 会跟随每个 chunk 传递。
        if document_id is not None:
            for doc in documents:
                doc.metadata["document_id"] = document_id

        split_documents = self._split_documents(documents)

        if not split_documents:
            raise ValueError(f"{file_path} 分片后没有有效文本内容")

        self.vector_store.add_documents(split_documents)

        self._save_md5_hex(md5_hex)

        # 重建 BM25 索引，保持与 Chroma 同步
        if self.hybrid_enabled:
            self._build_bm25_index()

        logger.info(f"[加载知识库] {file_path} 内容加载成功，chunks={len(split_documents)}")

        return len(split_documents)

    def load_document(self):
        """
        从 data 文件夹读取所有允许类型文件，批量入库。
        与参考项目保持一致，同时复用 load_single_file。
        """
        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        total = 0

        for path in allowed_files_path:
            try:
                count = self.load_single_file(path)
                total += count
            except Exception as e:
                logger.error(f"[加载知识库] {path} 加载失败：{str(e)}", exc_info=True)
                continue

        return total

    def search(self, query: str, top_k: int | None = None):
        """
        纯向量检索接口，返回 Document 列表。
        """
        if top_k is None:
            top_k = chroma_conf["k"]

        retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        return retriever.invoke(query)

    def _build_bm25_index(self):
        """
        从 Chroma 拉取所有 chunk 文本，构建 BM25 索引。

        BM25Retriever 的索引是内存中的，需要和 Chroma 保持同步。
        策略：每次写操作（增/删）后调用此方法重建索引。
        从 Chroma 拉取（而非自己维护副本）保证一致性。
        """
        all_data = self.vector_store.get()

        if not all_data["documents"]:
            self._bm25_retriever = None
            return

        documents = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(all_data["documents"], all_data["metadatas"])
        ]

        self._bm25_retriever = BM25Retriever.from_documents(documents, k=self.bm25_top_k)
        logger.info(f"BM25 索引重建完成，文档数: {len(documents)}")

    def _rrf_fusion(
        self,
        vector_docs: list[Document],
        bm25_docs: list[Document],
    ) -> list[Document]:
        """
        RRF（Reciprocal Rank Fusion）融合两组检索结果。

        RRF_score(d) = Σ 1 / (k + rank_i(d))

        为什么用 RRF 而不是加权平均？
        - RRF 不需要调权重参数，对两个检索器的分数尺度差异不敏感
        - 向量检索的余弦相似度和 BM25 的 BM25 分数量纲完全不同，直接加权不合理
        - RRF 只看排名位置，天然适配不同检索器的结果融合
        """
        doc_scores: dict[str, tuple[float, Document]] = {}

        for rank, doc in enumerate(vector_docs, start=1):
            key = doc.page_content[:100]
            score = 1.0 / (self.rrf_k + rank)
            if key in doc_scores:
                doc_scores[key] = (doc_scores[key][0] + score, doc_scores[key][1])
            else:
                doc_scores[key] = (score, doc)

        for rank, doc in enumerate(bm25_docs, start=1):
            key = doc.page_content[:100]
            score = 1.0 / (self.rrf_k + rank)
            if key in doc_scores:
                doc_scores[key] = (doc_scores[key][0] + score, doc_scores[key][1])
            else:
                doc_scores[key] = (score, doc)

        sorted_items = sorted(doc_scores.values(), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in sorted_items]

    def hybrid_search(self, query: str, top_k: int | None = None) -> list[Document]:
        """
        混合检索：向量检索 + BM25 检索 → RRF 融合。

        返回融合后的 top_k 个文档。
        """
        search_k = top_k or self.bm25_top_k

        # 向量检索
        vector_docs = self.search(query, top_k=search_k)

        # BM25 检索
        if self._bm25_retriever is None:
            self._build_bm25_index()

        if self._bm25_retriever:
            bm25_docs = self._bm25_retriever.invoke(query)
        else:
            bm25_docs = []

        if not bm25_docs:
            return vector_docs

        # RRF 融合
        fused_docs = self._rrf_fusion(vector_docs, bm25_docs)
        return fused_docs[:search_k]


    def delete_by_document_id(self, document_id: int):
        """
        根据 document_id 删除 Chroma 中对应的 chunks。

        前提：入库时每个 chunk 的 metadata 中已经写入 document_id。
        """
        self.vector_store.delete(where={"document_id": document_id})

        # 重建 BM25 索引，保持与 Chroma 同步
        if self.hybrid_enabled:
            self._build_bm25_index()

    def remove_md5_by_file_path(self, file_path: str):
        """
        根据文件路径计算 md5，并从 md5.text 中移除。
        """
        md5_hex = get_file_md5_hex(file_path)
        if md5_hex:
            self._remove_md5_hex(md5_hex)

    def count(self) -> int:
        """
        返回当前 collection 中的 chunk 数量。
        """
        return self.vector_store._collection.count()

    def clear(self):
        """
        清空向量库文件和 md5 记录。
        """
        persist_dir = get_abs_path(chroma_conf["persist_directory"])
        md5_store = self._md5_store_path()

        # 删除 Chroma 目录
        if os.path.exists(persist_dir):
            import shutil
            shutil.rmtree(persist_dir)

        os.makedirs(persist_dir, exist_ok=True)

        # 删除 md5 记录
        if os.path.exists(md5_store):
            os.remove(md5_store)

        # 重新初始化 Chroma
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=persist_dir,
        )

        # 清空 BM25 索引
        self._bm25_retriever = None
