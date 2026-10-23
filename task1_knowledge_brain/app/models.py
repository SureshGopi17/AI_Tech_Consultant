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
    prompt_used: Optional[str] = None
    thinking_trace: Optional[str] = None
    retrieval_chunks: List[Dict[str, Any]] = Field(default_factory=list)

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

class UpdateSitemapRequest(BaseModel):
    sitemap_url: str

class AddSitemapRequest(BaseModel):
    sitemap_url: str
    dashboard_id: Optional[str] = None

class VerifyUrlItem(BaseModel):
    id: str
    title: str
    url: str
    category: str
    summary: str
    status: str = "HTTP 200 OK (Verified)"
    http_code: int = 200
    lastmod: Optional[str] = None
    hash: str = ""
    screenshots_count: int = 0
    content_length: int = 0
    consecutive_failures: int = 0
    quarantine_level: Optional[str] = None  # None, QUARANTINE_301_REDIRECT, QUARANTINE_404_PURGED
    is_indexed: bool = True
    approved_by_human: bool = True
    discovered_at: Optional[str] = None
    parent_sitemap: Optional[str] = None

class VerifyUrlsResponse(BaseModel):
    total_urls: int
    verified_urls: List[VerifyUrlItem]
    checking_time_ms: float
    timestamp: str
    sitemap_url: str
    active_count: int = 0
    quarantined_count: int = 0
    pending_count: int = 0

# --- User Authentication Models ---
class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class UserSession(BaseModel):
    id: str
    name: str
    email: str
    role: str = "Lead AI Consultant"
    active_dashboard_id: str
    created_at: str

class AuthResponse(BaseModel):
    success: bool
    user: UserSession
    token: str
    message: str

# --- Knowledge Base Dashboards Models ---
class KnowledgeDashboard(BaseModel):
    id: str
    user_id: str
    name: str
    website_name: str
    sitemap_urls: List[str] = Field(default_factory=list)
    child_sitemaps: List[str] = Field(default_factory=list)
    description: str = ""
    consecutive_failure_threshold: int = 3  # Threshold X
    quarantine_action_rule: str = "quarantine_404_and_301"
    status: str = "LIVE / SYNCHRONIZED"
    created_at: str
    last_crawl_datetime: str = ""
    website_summary: str = ""
    main_topics: List[str] = Field(default_factory=list)

class CreateDashboardRequest(BaseModel):
    name: str
    website_name: str
    sitemap_urls: List[str]
    description: Optional[str] = ""
    consecutive_failure_threshold: int = 3

class UpdateDashboardRequest(BaseModel):
    name: Optional[str] = None
    website_name: Optional[str] = None
    sitemap_urls: Optional[List[str]] = None
    description: Optional[str] = None
    consecutive_failure_threshold: Optional[int] = None
    quarantine_action_rule: Optional[str] = None

# --- Reconciliation, Refresh Run, and Health Settings Models ---
class ReconciliationReport(BaseModel):
    discovered_count: int
    processed_count: int
    indexed_count: int
    skipped_count: int
    failed_count: int
    quarantined_count: int
    pending_count: int
    reconciliation_valid: bool = True
    audit_formula: str = "Discovered = Indexed + Pending + Skipped + Failed + Quarantined"
    generated_at: str

class RefreshRunReport(BaseModel):
    first_fetch_datetime: str
    last_fetch_datetime: str
    total_fetched_urls: int
    urls: List[VerifyUrlItem]
    duration_ms: float

class HealthSettingsRequest(BaseModel):
    consecutive_failure_threshold: int = 3  # Threshold X
    quarantine_action_rule: str = "quarantine_404_and_301"

class CrawlUrlsRequest(BaseModel):
    urls: List[str]
    force_reindex: bool = False

class ApproveUrlsRequest(BaseModel):
    urls: List[str]
    approved: bool = True

class DashboardSummaryResponse(BaseModel):
    dashboard_id: str
    dashboard_name: str
    website_name: str
    sitemap_urls: List[str]
    child_sitemaps: List[str]
    total_discovered: int
    successfully_crawled: int
    successfully_indexed: int
    pending_processing: int
    failed_urls: int
    skipped_duplicates: int
    quarantined_urls: int
    consecutive_failure_threshold: int
    last_crawl_datetime: str
    current_status: str
    website_summary: str
    main_topics: List[str]

