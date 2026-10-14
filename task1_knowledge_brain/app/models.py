"""
Pydantic data models for Task 1: The Knowledge Brain.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ArticleImage(BaseModel):
    url: str
    caption: str = ""
    alt_text: str = ""
    section: Optional[str] = None
    visual_tags: List[str] = Field(default_factory=list)

class Article(BaseModel):
    id: str
    url: str
    title: str
    category: str = "General"
    folder: str = "Documentation"
    content: str
    summary: str = ""
    images: List[ArticleImage] = Field(default_factory=list)
    lastmod: Optional[str] = None
    hash: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_deleted: bool = False

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

class SearchResultItem(BaseModel):
    article_id: str
    title: str
    url: str
    category: str
    folder: str
    snippet: str
    score: float
    images: List[ArticleImage] = Field(default_factory=list)

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total: int
    query: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = None

class Citation(BaseModel):
    title: str
    url: str
    category: str
    snippet: str

class ChatResponse(BaseModel):
    answer: str
    confidence: float
    can_answer: bool
    citations: List[Citation] = Field(default_factory=list)
    screenshots: List[ArticleImage] = Field(default_factory=list)
    escalation_id: Optional[str] = None
    model_used: str = "claude-3-5-sonnet"
    latency_ms: float = 0.0

class EscalationItem(BaseModel):
    id: str
    question: str
    confidence: float
    created_at: str
    status: str = "PENDING"  # PENDING, RESOLVED
    expert_answer: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None

class ResolveEscalationRequest(BaseModel):
    expert_answer: str
    notes: Optional[str] = None
    resolved_by: str = "Human Expert"

class SyncStatus(BaseModel):
    total_articles: int
    total_images: int
    last_sync: Optional[str]
    added_count: int = 0
    updated_count: int = 0
    removed_count: int = 0
    status: str = "idle"  # idle, syncing, completed, failed
