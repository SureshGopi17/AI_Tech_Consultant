"""
FastAPI Server for Task 1: The Knowledge Brain.
Offers clean REST APIs for Task 2 and Task 3, documentation at /docs,
and serves a clean, intuitive web interface.
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List

from app.config import settings
from app.models import (
    SearchQuery, SearchResponse, SearchResultItem,
    ChatRequest, ChatResponse,
    EscalationItem, ResolveEscalationRequest,
    SyncStatus, Article
)
from app.vector_store import knowledge_store
from app.rag_engine import rag_engine
from app.sitemap_sync import sitemap_synchronizer
from app.escalations import escalation_manager

app = FastAPI(
    title="The Knowledge Brain API",
    version="1.0.0",
    description="Intelligent public help center memory and RAG API for Brilliant Directories."
)

# CORS enabled for all origins (Task 2 & 3 access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for UI
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_home():
    """Serves the simple, clear user screen for the Knowledge Brain."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Knowledge Brain API is running. Visit /docs for OpenAPI documentation."}

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Task 1 - The Knowledge Brain",
        "total_articles": len(knowledge_store.articles),
        "total_images": sum(len(a.images) for a in knowledge_store.articles.values()),
        "last_sync": sitemap_synchronizer.last_sync_time or "Initialized"
    }

@app.post("/api/v1/search", response_model=SearchResponse)
def search_knowledge_base(query: SearchQuery):
    """
    Core search endpoint for Task 2 (Inbox Agent) and Task 3 (Scope of Work).
    Returns ranked documentation chunks, citations, and screenshot references.
    """
    results = knowledge_store.search(
        query=query.query,
        top_k=query.top_k,
        category=query.category
    )
    return SearchResponse(
        results=results,
        total=len(results),
        query=query.query
    )

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat_with_brain(request: ChatRequest):
    """
    Chatbot endpoint. Answers questions, provides exact article citations,
    identifies screenshots, and creates expert escalations when uncertain.
    """
    return rag_engine.ask(request)

@app.get("/api/v1/articles", response_model=List[Article])
def list_articles(category: Optional[str] = None, limit: int = 50):
    """Returns indexed articles with their multimodal screenshots."""
    arts = list(knowledge_store.articles.values())
    if category:
        arts = [a for a in arts if a.category.lower() == category.lower()]
    return arts[:limit]

@app.get("/api/v1/articles/{article_id}", response_model=Article)
def get_article(article_id: str):
    for art in knowledge_store.articles.values():
        if art.id == article_id:
            return art
    raise HTTPException(status_code=404, detail="Article not found")

@app.post("/api/v1/sync", response_model=SyncStatus)
def trigger_daily_sync(max_scrapes: int = Query(5, ge=1, le=50)):
    """Triggers differential sitemap sync to keep knowledge fresh."""
    return sitemap_synchronizer.run_differential_sync(max_new_scrapes=max_scrapes)

@app.get("/api/v1/sync/status", response_model=SyncStatus)
def get_sync_status():
    total_articles = len(knowledge_store.articles)
    total_images = sum(len(a.images) for a in knowledge_store.articles.values())
    return SyncStatus(
        total_articles=total_articles,
        total_images=total_images,
        last_sync=sitemap_synchronizer.last_sync_time or "Initialized",
        status="completed"
    )

@app.get("/api/v1/escalations", response_model=List[EscalationItem])
def list_escalations(status: Optional[str] = None):
    """Lists human expert escalation tasks (unanswered chatbot queries)."""
    return escalation_manager.list_escalations(status)

@app.post("/api/v1/escalations/{esc_id}/resolve", response_model=EscalationItem)
def resolve_escalation(esc_id: str, payload: ResolveEscalationRequest):
    """
    Human expert resolves an unanswered task.
    The expert's verified answer immediately flows back into the knowledge memory.
    """
    esc = escalation_manager.resolve_escalation(
        esc_id=esc_id,
        expert_answer=payload.expert_answer,
        resolved_by=payload.resolved_by
    )
    if not esc:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    # Flow answer back into knowledge brain memory
    knowledge_store.add_expert_answer(
        question=esc.question,
        answer=payload.expert_answer,
        expert_name=payload.resolved_by
    )
    return esc

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
