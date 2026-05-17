"""
FastAPI 后端入口。

启动：
uvicorn backend.app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.rag import router as rag_router

app = FastAPI(
    title="Remote Sensing RAG API",
    description="参考 agent.zip 项目结构重构的 FastAPI + Streamlit + LangChain RAG 项目。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)


@app.get("/health")
def health():
    return {"status": "ok"}
