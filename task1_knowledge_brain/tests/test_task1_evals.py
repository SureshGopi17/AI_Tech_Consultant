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
