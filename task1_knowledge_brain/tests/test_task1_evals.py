"""
Comprehensive Evaluation Suite for Task 1: The Knowledge Brain.
Contains 22 rigorous automated test cases evaluating:
- Factual retrieval accuracy across domains
- Multimodal screenshot extraction
- Honest "I don't know" out-of-domain guardrails
- Human-in-the-loop escalation flow back into memory
- Sitemap article removal safety
- Speed / latency benchmarks & schema adherence
"""

import pytest
import time
import os
import sys

# Ensure task1_knowledge_brain root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.vector_store import knowledge_store
from app.rag_engine import rag_engine
from app.models import ChatRequest, SearchQuery
from app.escalations import escalation_manager
from app.sitemap_sync import sitemap_synchronizer
from app.seed_data import SEED_ARTICLES

@pytest.fixture(autouse=True)
def reset_clean_state():
    """Ensures each test runs against a clean, isolated knowledge state."""
    knowledge_store.articles = {art.url: art for art in SEED_ARTICLES}
    knowledge_store.expert_qa_memory = []
    knowledge_store._rebuild_chunks_index()
    escalation_manager.escalations = []
    from app.kb_manager import kb_manager
    kb_manager._initialize_url_inventory_from_seeds()
    yield

# 1. Core Knowledge Retrieval Tests (15 domains)

def test_01_search_stripe_billing_setup():
    res = knowledge_store.search("How do I set up Stripe for automatic recurring member billing?", top_k=3)
    assert len(res) > 0
    top = res[0]
    assert "stripe" in top.title.lower() or "billing" in top.title.lower()
    assert top.score >= 0.50
    assert any("stripe" in img.visual_tags for img in top.images)

def test_02_search_distance_metric_change():
    res = knowledge_store.search("Change search distance radius from miles to kilometers", top_k=3)
    assert len(res) > 0
    assert "kilometer" in res[0].title.lower() or "miles" in res[0].title.lower()
    assert res[0].score >= 0.50

def test_03_search_custom_fields_signup():
    res = knowledge_store.search("How to add custom fields to member signup registration form?", top_k=3)
    assert len(res) > 0
    assert "custom field" in res[0].title.lower() or "form" in res[0].title.lower()

def test_04_search_auto_lead_routing():
    res = knowledge_store.search("Auto lead distribution and matching rules for members", top_k=3)
    assert len(res) > 0
    assert "lead" in res[0].title.lower()

def test_05_search_category_csv_import():
    res = knowledge_store.search("Import member categories and sub categories using CSV file", top_k=3)
    assert len(res) > 0
    assert "categor" in res[0].title.lower()

def test_06_search_bulk_member_import():
    res = knowledge_store.search("Bulk import 500 members from CSV spreadsheet with geocoding", top_k=3)
    assert len(res) > 0
    assert "import" in res[0].title.lower() and "member" in res[0].title.lower()

def test_07_search_google_tag_manager_ga4():
    res = knowledge_store.search("Where to enter Google Tag Manager GTM container code or GA4 ID?", top_k=3)
    assert len(res) > 0
    assert "google tag manager" in res[0].title.lower() or "gtm" in res[0].snippet.lower()

def test_08_search_review_moderation_approval():
    res = knowledge_store.search("Enable member review moderation so reviews require admin approval", top_k=3)
    assert len(res) > 0
    assert "review" in res[0].title.lower()

def test_09_search_welcome_email_templates():
    res = knowledge_store.search("Customize automated welcome email template with dynamic merge tags", top_k=3)
    assert len(res) > 0
    assert "email" in res[0].title.lower()

def test_10_search_claim_unclaimed_listing():
    res = knowledge_store.search("How members claim existing unclaimed listings and upgrade to paid", top_k=3)
    assert len(res) > 0
    assert "claim" in res[0].title.lower()

def test_11_search_private_directory_access():
    res = knowledge_store.search("Restrict member search results to logged in members only", top_k=3)
    assert len(res) > 0
    assert "restrict" in res[0].title.lower() or "privacy" in res[0].category.lower()

def test_12_search_outbound_webhooks_crm():
    res = knowledge_store.search("Configure outbound webhooks to sync member signups to Zapier or CRM", top_k=3)
    assert len(res) > 0
    assert "webhook" in res[0].title.lower()

def test_13_search_discount_promo_coupons():
    res = knowledge_store.search("Create discount coupon codes for 20 percent off membership renewals", top_k=3)
    assert len(res) > 0
    assert "coupon" in res[0].title.lower() or "promo" in res[0].title.lower()

def test_14_search_video_reels_embed():
    res = knowledge_store.search("Embed YouTube and Vimeo showreel videos on member profile pages", top_k=3)
    assert len(res) > 0
    assert "video" in res[0].title.lower()

def test_15_search_member_cancellation_refund():
    res = knowledge_store.search("Issue full or partial refund to member credit card via Stripe", top_k=3)
    assert len(res) > 0
    assert "refund" in res[0].title.lower() or "cancellation" in res[0].title.lower()

# 2. Multimodal Screenshot Verification
def test_16_multimodal_screenshot_retrieval():
    res = knowledge_store.search("Stripe payment gateway", top_k=1)
    assert len(res) > 0
    assert len(res[0].images) > 0
    img = res[0].images[0]
    assert img.url.startswith("http")
    assert len(img.visual_tags) > 0
    assert img.caption != ""

# 3. Honest Guardrails & Out-of-Domain Detection
def test_17_honest_rejection_out_of_domain():
    req = ChatRequest(message="What is the authentic recipe for Italian carbonara pasta?")
    resp = rag_engine.ask(req)
    assert resp.can_answer is False
    assert resp.confidence < 0.60
    assert "do not have sufficient information" in resp.answer.lower()
    assert resp.escalation_id is not None
    assert resp.escalation_id.startswith("ESC-")

def test_18_honest_rejection_low_confidence():
    req = ChatRequest(message="How do I launch a SpaceX Falcon 9 rocket from Brilliant Directories?")
    resp = rag_engine.ask(req)
    assert resp.can_answer is False
    assert resp.confidence < 0.50
    assert resp.escalation_id is not None

# 4. Human-in-the-Loop Feedback Loop: Expert Answer Flows Back to Memory
def test_19_human_escalation_flow_back_into_memory():
    unique_question = "How do we integrate biometric iris scanning into lawyer member checkins?"
    
    # Step 1: Initial ask fails honestly
    req1 = ChatRequest(message=unique_question)
    resp1 = rag_engine.ask(req1)
    assert resp1.can_answer is False
    esc_id = resp1.escalation_id
    assert esc_id is not None

    # Step 2: Human expert provides verified solution
    verified_answer = "Iris scanning can be integrated by linking an external WebAuthn FIDO2 biometric endpoint to the BD Custom Header widget."
    esc = escalation_manager.resolve_escalation(
        esc_id=esc_id,
        expert_answer=verified_answer,
        resolved_by="Chief Security Architect"
    )
    assert esc.status == "RESOLVED"
    
    # Store in memory
    knowledge_store.add_expert_answer(unique_question, verified_answer)

    # Step 3: Second ask immediately succeeds with top confidence!
    req2 = ChatRequest(message=unique_question)
    resp2 = rag_engine.ask(req2)
    assert resp2.can_answer is True
    assert resp2.confidence >= 0.90
    assert "iris scanning can be integrated" in resp2.answer.lower()

# 5. Requirement: A removed article must stop appearing in answers
def test_20_removed_article_purged_from_answers():
    target_url = "https://support.brilliantdirectories.com/support/solutions/articles/5000558445-embed-video-reels-youtube-vimeo"
    
    # Verify it exists initially
    assert target_url in knowledge_store.articles
    initial_res = knowledge_store.search("YouTube Vimeo video showreel embed", top_k=2)
    assert any(r.url == target_url for r in initial_res)

    # Simulate removal from sitemap
    sitemap_synchronizer.simulate_removal_test(target_url)

    # Verify it is purged
    assert target_url not in knowledge_store.articles
    after_res = knowledge_store.search("YouTube Vimeo video showreel embed", top_k=5)
    assert not any(r.url == target_url for r in after_res), "Removed article must NOT appear in search results!"

# 6. Performance & SLA Benchmarks
def test_21_speed_and_latency_sla():
    start = time.time()
    req = ChatRequest(message="How to connect Stripe payments?")
    resp = rag_engine.ask(req)
    latency_ms = (time.time() - start) * 1000
    assert resp.can_answer is True
    # Fast local latency target < 250ms
    assert latency_ms < 250, f"Query took too long: {latency_ms}ms"

def test_22_api_contract_and_clean_json_schema():
    req = ChatRequest(message="How to bulk import members via CSV?")
    resp = rag_engine.ask(req)
    assert isinstance(resp.answer, str) and len(resp.answer) > 20
    assert isinstance(resp.confidence, float)
    assert isinstance(resp.can_answer, bool)
    assert isinstance(resp.citations, list)
    assert len(resp.citations) > 0
    cit = resp.citations[0]
    assert cit.url.startswith("https://")
    assert cit.title != ""

# 7. New Scope Evals: Pre-flight Analysis, Archiving (Never Deleted), Multi-sitemap & 301 Follower
def test_23_preflight_sitemap_analysis_summary():
    from app.kb_manager import kb_manager
    pf = kb_manager.analyze_sitemaps()
    assert pf.total_sitemaps_found >= 1
    assert pf.total_urls_found >= 15
    assert pf.first_url is not None and pf.first_url.startswith("http")
    assert pf.last_url is not None and pf.last_url.startswith("http")
    assert pf.pages_per_one_hour == 240
    assert pf.pages_per_hour == 240
    assert pf.pages_per_day == 5760
    assert pf.expected_completion_time_sec > 0
    assert pf.requires_user_confirmation is True
    assert len(pf.nested_sitemaps) > 0
    child = pf.nested_sitemaps[0]
    assert child.url_count >= 0
    assert child.status == "accessible"

def test_24_confirm_ingest_user_confirmation():
    from app.kb_manager import kb_manager
    conf = kb_manager.confirm_ingestion(dash_id="dash-bd-prod-01")
    assert conf.success is True
    assert conf.pages_crawled > 0
    assert conf.pages_indexed > 0
    assert conf.status == "COMPLETED_AND_SYNCHRONIZED"

def test_25_archived_knowledge_store_never_deleted():
    from app.kb_manager import kb_manager
    # 1. Verify archived store has items and invariant is True
    arch_resp = kb_manager.get_archived_urls()
    assert arch_resp.never_deleted_invariant is True
    assert arch_resp.total_archived >= 1
    sample_arch = arch_resp.archived_urls[0]
    assert sample_arch.archived_reason != ""

    # 2. Test restore functionality
    restore_res = kb_manager.restore_archived_urls([sample_arch.url])
    assert restore_res["success"] is True
    assert sample_arch.url in kb_manager.url_inventory
    assert kb_manager.url_inventory[sample_arch.url]["is_indexed"] is True

def test_26_multi_sitemap_duplicate_detection():
    from app.kb_manager import kb_manager
    all_urls = kb_manager.get_all_urls(filter_type="all")
    dups = [u for u in all_urls if u.is_duplicate_across_sitemaps or len(u.referencing_sitemaps) > 1]
    assert len(dups) > 0
    for d in dups:
        assert len(d.referencing_sitemaps) >= 2

def test_27_301_redirect_destination_followed_and_indexed():
    from app.kb_manager import kb_manager
    all_urls = kb_manager.get_all_urls(filter_type="all")
    redir_301 = [u for u in all_urls if u.http_code == 301 or "301" in u.status]
    assert len(redir_301) > 0
    item = redir_301[0]
    assert item.redirect_target is not None
    assert item.redirect_target.startswith("https://")
    # Verify target destination is active in inventory
    assert item.redirect_target in kb_manager.url_inventory

# 8. JWT Authentication & Comprehensive RAG Answer Synthesis Evals
def test_28_jwt_authentication_token_creation_and_claims():
    from app.auth import create_access_token, decode_access_token
    from app.models import UserSession
    session = UserSession(
        id="user-test-jwt",
        name="Test Lead Consultant",
        email="consultant-eval@tech.ai",
        role="Lead AI Consultant",
        active_dashboard_id="dash-bd-prod-01",
        created_at="2026-10-23 00:00:00 UTC"
    )
    token = create_access_token(session)
    assert isinstance(token, str) and len(token) > 50
    claims = decode_access_token(token)
    assert claims["sub"] == "user-test-jwt"
    assert claims["email"] == "consultant-eval@tech.ai"
    assert claims["role"] == "Lead AI Consultant"
    assert claims["aud"] == "knowledge-brain-users"
    assert claims["exp"] > claims["iat"]

def test_29_knowledge_brain_rich_step_by_step_response_synthesis():
    req = ChatRequest(message="How do I connect Stripe payment gateway and enable recurring billing?")
    resp = rag_engine.ask(req)
    assert resp.can_answer is True
    assert resp.confidence >= 0.85
    assert len(resp.citations) > 0
    # Complete un-truncated step-by-step instructions check
    assert "Settings > General Settings > Payments" in resp.answer
    assert "Publishable Key" in resp.answer
    assert "Webhook" in resp.answer
    # Must have detailed structured Markdown headings
    assert "### Official Solution:" in resp.answer
    assert "#### Step-by-Step Instructions:" in resp.answer

def test_30_jwt_auth_api_endpoint_integration():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    # 1. Demo Login returning JWT
    login_resp = client.post("/api/v1/auth/demo-login")
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["success"] is True
    assert "token" in data
    assert data["token_type"] == "bearer"
    token = data["token"]
    
    # 2. Authenticated verify-token with Bearer header
    headers = {"Authorization": f"Bearer {token}"}
    verify_resp = client.post("/api/v1/auth/verify-token", headers=headers)
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["valid"] is True
    assert v_data["user"]["email"] == "suresh@consultant.ai"
    assert v_data["algorithm"] == "HS256"
