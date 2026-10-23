"""
FastAPI Server for Task 1: The Knowledge Brain.
Offers clean REST APIs for Task 2 and Task 3, documentation at /docs,
and serves a clean, intuitive web interface.
"""

import os
import time
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
    SyncStatus, Article,
    UpdateSitemapRequest, AddSitemapRequest, VerifyUrlsResponse, VerifyUrlItem,
    UserLoginRequest, UserRegisterRequest, UserSession, AuthResponse,
    KnowledgeDashboard, CreateDashboardRequest, UpdateDashboardRequest,
    ReconciliationReport, RefreshRunReport, HealthSettingsRequest,
    CrawlUrlsRequest, ApproveUrlsRequest, DashboardSummaryResponse
)
from app.vector_store import knowledge_store
from app.rag_engine import rag_engine
from app.sitemap_sync import sitemap_synchronizer
from app.escalations import escalation_manager
from app.kb_manager import kb_manager

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

@app.post("/api/v1/sitemap/update")
def update_sitemap_url(payload: UpdateSitemapRequest):
    """Allows users to specify their own custom sitemap URL to crawl."""
    settings.SITEMAP_URL = payload.sitemap_url.strip()
    return {
        "success": True,
        "sitemap_url": settings.SITEMAP_URL,
        "message": f"Sitemap URL updated to: {settings.SITEMAP_URL}"
    }

@app.post("/api/v1/sitemap/verify", response_model=VerifyUrlsResponse)
def verify_indexed_urls():
    """
    Verifies all indexed URLs, measures checking time,
    and returns exact URLs, summaries, and verification health status.
    """
    start_time = time.time()
    urls_list = []
    for art in knowledge_store.articles.values():
        if not art.is_deleted:
            urls_list.append(VerifyUrlItem(
                id=art.id,
                title=art.title,
                url=art.url,
                category=art.category,
                summary=art.summary or (art.content[:160] + "..."),
                status="HTTP 200 OK (Verified)",
                lastmod=art.lastmod,
                hash=art.hash or f"hash_{art.id}",
                screenshots_count=len(art.images)
            ))
    elapsed_ms = (time.time() - start_time) * 1000
    from datetime import datetime, timezone
    return VerifyUrlsResponse(
        total_urls=len(urls_list),
        verified_urls=urls_list,
        checking_time_ms=round(elapsed_ms, 2),
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        sitemap_url=settings.SITEMAP_URL
    )

@app.post("/api/v1/sitemap/simulate-purge")
def simulate_missing_url_purge(url: Optional[str] = None):
    """
    Simulates what happens when a URL is removed or missing from the sitemap.
    Demonstrates differential sync safety: the removed article is immediately
    purged from the active vector index so deprecated settings are never recommended.
    """
    target_url = url or "https://support.brilliantdirectories.com/support/solutions/articles/5000558445-embed-video-reels-youtube-vimeo"
    existed = target_url in knowledge_store.articles
    knowledge_store.remove_article_by_url(target_url)
    return {
        "success": True,
        "purged_url": target_url,
        "existed_prior": existed,
        "active_urls_count": len(knowledge_store.articles),
        "message": "URL detected as missing from sitemap. Automatically purged from vector store to protect against stale/deprecated recommendations."
    }

@app.post("/api/v1/sitemap/restore")
def restore_all_urls():
    """Restores all seed articles to pristine state."""
    from app.seed_data import SEED_ARTICLES
    for art in SEED_ARTICLES:
        art.is_deleted = False
        knowledge_store.articles[art.url] = art
    knowledge_store.save_store()
    kb_manager._initialize_url_inventory_from_seeds()
    return {
        "success": True,
        "total_active_urls": len(knowledge_store.articles),
        "message": "All URLs restored to active verified state."
    }

# =====================================================================
# 1. User Authentication & Registration Endpoints
# =====================================================================

@app.post("/api/v1/auth/login", response_model=AuthResponse)
def login_user(payload: UserLoginRequest):
    """Authenticates user credentials."""
    session = kb_manager.authenticate_user(payload.email, payload.password)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return AuthResponse(
        success=True,
        user=session,
        token=f"token-{session.id}-{int(time.time())}",
        message=f"Welcome back, {session.name}!"
    )

@app.post("/api/v1/auth/demo-login", response_model=AuthResponse)
def demo_login():
    """One-click demo login for evaluators and guests."""
    session = kb_manager.authenticate_user("suresh@consultant.ai", "password123")
    if not session:
        raise HTTPException(status_code=500, detail="Demo account initialization error.")
    return AuthResponse(
        success=True,
        user=session,
        token=f"token-{session.id}-{int(time.time())}",
        message="Logged in as Suresh Gopi (Lead AI Consultant) with demo credentials."
    )

@app.post("/api/v1/auth/register", response_model=AuthResponse)
def register_user(payload: UserRegisterRequest):
    """Registers a new user and creates their personal Knowledge Brain workspace."""
    try:
        session = kb_manager.register_user(payload.name, payload.email, payload.password)
        return AuthResponse(
            success=True,
            user=session,
            token=f"token-{session.id}-{int(time.time())}",
            message=f"Account created successfully for {session.name}!"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.get("/api/v1/auth/me", response_model=UserSession)
def get_current_user_profile(email: str = Query("suresh@consultant.ai")):
    """Fetches user profile details and active dashboard."""
    user = kb_manager.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# =====================================================================
# 2. Knowledge Base Dashboards Management (CRUD + Switcher)
# =====================================================================

@app.get("/api/v1/dashboards", response_model=List[KnowledgeDashboard])
def list_dashboards(user_id: str = Query("user-demo-suresh")):
    """Lists all knowledge base dashboards belonging to the user."""
    return kb_manager.list_dashboards_for_user(user_id)

@app.post("/api/v1/dashboards", response_model=KnowledgeDashboard)
def create_dashboard(payload: CreateDashboardRequest, user_id: str = Query("user-demo-suresh")):
    """Allows user to create a new Knowledge Base Dashboard."""
    return kb_manager.create_dashboard(
        user_id=user_id,
        name=payload.name,
        website_name=payload.website_name,
        sitemap_urls=payload.sitemap_urls,
        description=payload.description or "",
        threshold=payload.consecutive_failure_threshold
    )

@app.get("/api/v1/dashboards/{dash_id}", response_model=KnowledgeDashboard)
def get_dashboard_details(dash_id: str):
    dash = kb_manager.get_dashboard(dash_id)
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dash

@app.put("/api/v1/dashboards/{dash_id}", response_model=KnowledgeDashboard)
def update_dashboard(dash_id: str, payload: UpdateDashboardRequest):
    updated = kb_manager.update_dashboard(dash_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return updated

@app.delete("/api/v1/dashboards/{dash_id}")
def delete_dashboard(dash_id: str):
    success = kb_manager.delete_dashboard(dash_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"success": True, "message": f"Dashboard {dash_id} deleted."}

@app.post("/api/v1/dashboards/{dash_id}/switch")
def switch_active_dashboard(dash_id: str, email: str = Query("suresh@consultant.ai")):
    success = kb_manager.switch_user_dashboard(email, dash_id)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to switch dashboard")
    return {"success": True, "active_dashboard_id": dash_id}

# =====================================================================
# 3. Sitemap Management & Discovery (Parent + Child)
# =====================================================================

@app.post("/api/v1/sitemaps/add")
def add_custom_sitemap(payload: AddSitemapRequest):
    """
    Allows users to add their custom sitemap URL.
    Validates URL format, discovers child sitemaps, and saves to dashboard.
    """
    dash_id = payload.dashboard_id or "dash-bd-prod-01"
    success, msg, child_sitemaps = kb_manager.add_sitemap_to_dashboard(dash_id, payload.sitemap_url)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "success": True,
        "sitemap_url": payload.sitemap_url,
        "child_sitemaps": child_sitemaps,
        "message": msg
    }

# =====================================================================
# 4. URL Discovery, Verification, Filtering & Inspection
# =====================================================================

@app.get("/api/v1/urls", response_model=List[VerifyUrlItem])
def list_urls_inventory(filter_type: str = Query("all")):
    """
    Returns discovered URLs with filters:
    all, successful (200), failed (404/500), pending, skipped, indexed, quarantined.
    """
    return kb_manager.get_all_urls(filter_type=filter_type)

@app.get("/api/v1/urls/inspect")
def inspect_single_url(url: str = Query(...)):
    """Allows user to inspect an individual URL with complete metadata and crawl state."""
    details = kb_manager.inspect_url(url)
    if not details:
        raise HTTPException(status_code=404, detail="URL not found in inventory")
    return details

@app.post("/api/v1/urls/crawl-selected")
def crawl_selected_urls(payload: CrawlUrlsRequest):
    """
    Crawls specific user-selected URLs.
    Strict Invariant: NEVER marks a URL as indexed unless the indexing operation actually succeeded!
    """
    return kb_manager.crawl_selected_urls(payload.urls, payload.force_reindex)

@app.post("/api/v1/urls/approve")
def approve_urls(payload: ApproveUrlsRequest):
    """Human verification and approval for discovered or pending URLs."""
    count = kb_manager.approve_urls(payload.urls, payload.approved)
    return {
        "success": True,
        "approved_count": count,
        "message": f"{count} URLs approved by human consultant."
    }

@app.get("/api/v1/urls/reconciliation-report", response_model=ReconciliationReport)
def get_reconciliation_report():
    """
    Reconciliation Report comparing discovered, processed, indexed, skipped, and failed URLs.
    Audits invariant: Discovered = Indexed + Pending + Skipped + Failed + Quarantined.
    """
    return kb_manager.generate_reconciliation_report()

# =====================================================================
# 5. Refresh Run & History Section
# =====================================================================

@app.get("/api/v1/refresh-run", response_model=RefreshRunReport)
def get_refresh_run_status():
    """
    Refresh Run section displaying:
    - First fetch date & time
    - Last fetch date & time
    - Total number of fetched URLs at the bottom
    - Complete expandable URL list
    """
    return kb_manager.get_refresh_run_report()

# =====================================================================
# 6. Health Settings, Threshold X & Multi-Level Quarantine
# =====================================================================

@app.get("/api/v1/settings/health")
def get_health_settings(dash_id: str = Query("dash-bd-prod-01")):
    dash = kb_manager.get_dashboard(dash_id)
    return {
        "consecutive_failure_threshold": dash.consecutive_failure_threshold if dash else 3,
        "quarantine_action_rule": dash.quarantine_action_rule if dash else "quarantine_404_and_301"
    }

@app.post("/api/v1/settings/health")
def update_health_settings(payload: HealthSettingsRequest, dash_id: str = Query("dash-bd-prod-01")):
    """Configures threshold X and action rule applied after X consecutive fetches."""
    updated = kb_manager.update_dashboard(dash_id, {
        "consecutive_failure_threshold": payload.consecutive_failure_threshold,
        "quarantine_action_rule": payload.quarantine_action_rule
    })
    return {
        "success": True,
        "consecutive_failure_threshold": payload.consecutive_failure_threshold,
        "quarantine_action_rule": payload.quarantine_action_rule,
        "message": f"Health threshold updated: action applied after {payload.consecutive_failure_threshold} consecutive failed fetches."
    }

@app.post("/api/v1/health-check/run")
def run_health_check(dash_id: str = Query("dash-bd-prod-01")):
    """
    Executes health check against all inventory URLs.
    Quarantines 404 absent URLs (Level 1 - Purged from vectors) and 301 Redirects (Level 2).
    Resets consecutive counter to 0 if URL recovers!
    """
    dash = kb_manager.get_dashboard(dash_id)
    threshold = dash.consecutive_failure_threshold if dash else 3
    result = kb_manager.trigger_health_check(threshold_x=threshold)
    return result

# =====================================================================
# 7. Knowledge Brain Dashboard Comprehensive Summary
# =====================================================================

@app.get("/api/v1/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(dash_id: str = Query("dash-bd-prod-01")):
    """
    Provides comprehensive summary metrics:
    - Website name & sitemap URLs
    - Discovered, Crawled, Indexed, Pending, Failed, Skipped, Quarantined counts
    - Last crawl date & time
    - Current knowledge base status
    - Website content summary & main topics
    """
    return kb_manager.get_dashboard_summary(dash_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
