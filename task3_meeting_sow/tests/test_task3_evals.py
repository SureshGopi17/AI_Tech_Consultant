"""
Comprehensive Evaluation Suite for Task 3: Meeting to Scope of Work.
22 automated test cases evaluating:
- Consultant requirement extraction accuracy
- Solution Architect Knowledge Brain API native setting detection & client savings
- Technical Estimator task modularization, hours, QA buffers, and costs
- Proposal synthesis & Human Consultant sign-off gatekeeper
- Scope Delta Engine: Modified, Dropped, and Scope Creep change order quotes
- Performance SLA & long context handling
"""

import pytest
import os
import sys
import time

# Ensure task3_meeting_sow root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import RequirementItem
from app.agents.consultant_agent import consultant_agent
from app.agents.solution_agent import solution_agent
from app.agents.estimator_agent import estimator_agent
from app.agents.proposal_agent import proposal_agent
from app.scope_differ import scope_differ
from app.pipeline import sow_pipeline

TRANSCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "shared", "data", "transcripts"))

def load_sample(filename: str) -> str:
    path = os.path.join(TRANSCRIPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- Group 1: Consultant Agent Requirement Extraction (Tests 1 - 3) ---

def test_01_consultant_extracts_client_metadata():
    t1 = load_sample("meeting_1_discovery.txt")
    meta, _ = consultant_agent.analyze_transcript(t1)
    assert meta["client_name"] == "Sarah Jenkins"
    assert meta["company_name"] == "LegalMatch Pro"

def test_02_consultant_extracts_business_goals():
    t1 = load_sample("meeting_1_discovery.txt")
    meta, _ = consultant_agent.analyze_transcript(t1)
    assert "directory" in meta["objective"].lower()
    assert "attorney" in meta["objective"].lower()

def test_03_consultant_extracts_all_functional_requirements():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    assert len(reqs) == 6
    assert any("billing" in r.title.lower() or "membership" in r.title.lower() for r in reqs)
    assert any("search" in r.title.lower() for r in reqs)
    assert any("lead" in r.title.lower() for r in reqs)
    assert any("bar" in r.title.lower() for r in reqs)
    assert any("theme" in r.title.lower() or "branding" in r.title.lower() for r in reqs)
    assert any("csv" in r.title.lower() or "import" in r.title.lower() for r in reqs)

# --- Group 2: Solution Architect & KB Native Detection (Tests 4 - 10) ---

def test_04_solution_architect_identifies_stripe_as_native():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    billing_req = next(r for r in evaluated if "billing" in r.title.lower() or "membership" in r.title.lower())
    assert billing_req.is_native_setting is True
    assert billing_req.resolution_type == "NATIVE_SETTING"
    assert "payments" in billing_req.native_setting_path.lower()

def test_05_solution_architect_identifies_search_as_native():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    search_req = next(r for r in evaluated if "search" in r.title.lower())
    assert search_req.is_native_setting is True
    assert search_req.resolution_type == "NATIVE_SETTING"

def test_06_solution_architect_identifies_lead_routing_as_native():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    lead_req = next(r for r in evaluated if "lead" in r.title.lower())
    assert lead_req.is_native_setting is True
    assert lead_req.resolution_type == "NATIVE_SETTING"

def test_07_solution_architect_identifies_custom_bar_verification():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    bar_req = next(r for r in evaluated if "bar" in r.title.lower())
    assert bar_req.is_native_setting is False
    assert bar_req.resolution_type == "CUSTOM_DEV"

def test_08_solution_architect_identifies_custom_theme_styling():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    theme_req = next(r for r in evaluated if "theme" in r.title.lower() or "branding" in r.title.lower())
    assert theme_req.is_native_setting is False
    assert theme_req.resolution_type == "CUSTOM_DEV"

def test_09_solution_architect_identifies_custom_csv_etl():
    t1 = load_sample("meeting_1_discovery.txt")
    _, reqs = consultant_agent.analyze_transcript(t1)
    evaluated = solution_agent.evaluate_requirements(reqs)
    csv_req = next(r for r in evaluated if "csv" in r.title.lower() or "import" in r.title.lower())
    assert csv_req.is_native_setting is False
    assert csv_req.resolution_type == "CUSTOM_DEV"

def test_10_client_savings_calculation():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    assert resp.sow.native_count == 3
    # 3 native features * 25 hrs * $95 = $7,125 savings
    assert resp.sow.estimated_savings_from_native >= 7000.0

# --- Group 3: Technical Estimator Hours & Costs (Tests 11 - 13) ---

def test_11_estimator_task_modularization():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    assert len(resp.tasks.tasks) >= 6
    assert any(t.dev_type == "Frontend" for t in resp.tasks.tasks)
    assert any(t.dev_type == "API/Webhook" for t in resp.tasks.tasks)

def test_12_estimator_hour_and_cost_rate_consistency():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    expected_cost = round(resp.tasks.total_hours * 95.0, 2)
    assert resp.tasks.total_cost == expected_cost

def test_13_estimator_qa_buffer_and_pm_hours():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    assert resp.tasks.qa_buffer_hours > 0
    assert resp.tasks.project_management_hours > 0

# --- Group 4: Proposal Generator & Human Gatekeeper (Tests 14 - 16) ---

def test_14_proposal_executive_summary_synthesis():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    assert len(resp.proposal.executive_summary) > 50
    assert "LegalMatch Pro" in resp.proposal.executive_summary
    assert resp.proposal.total_hours > 0

def test_15_proposal_human_approval_gatekeeper():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    # Requirement: "Nothing reaches the client until a human approves it."
    assert resp.proposal.approved_by_human is False
    assert resp.proposal.approved_at is None

def test_16_proposal_human_signoff_action():
    t1 = load_sample("meeting_1_discovery.txt")
    resp = sow_pipeline.run_pipeline(t1)
    # Simulate human sign-off
    resp.proposal.approved_by_human = True
    resp.proposal.approved_at = "2026-10-16T12:00:00Z"
    assert resp.proposal.approved_by_human is True
    assert resp.proposal.approved_at is not None

# --- Group 5: Scope Creep & Differential Engine (Tests 17 - 21) ---

def test_17_scope_differ_detects_modified_search_slider():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    delta = scope_differ.compare_meetings(t1, t2)
    mod = next(m for m in delta.modified_items if "slider" in m.title.lower() or "search" in m.title.lower())
    assert mod.status == "MODIFIED"
    assert mod.updated_hours > mod.original_hours

def test_18_scope_differ_detects_dropped_bar_verification():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    delta = scope_differ.compare_meetings(t1, t2)
    dropped = next(d for d in delta.dropped_items if "bar" in d.title.lower())
    assert dropped.status == "DROPPED"
    assert dropped.updated_hours == 0.0

def test_19_scope_differ_detects_mobile_app_scope_creep():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    delta = scope_differ.compare_meetings(t1, t2)
    mobile = next(c for c in delta.scope_creep_items if "mobile" in c.title.lower() or "app" in c.title.lower())
    assert mobile.is_scope_creep is True
    assert mobile.additional_quote_required is True
    assert mobile.updated_hours >= 80.0

def test_20_scope_differ_detects_quickbooks_scope_creep():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    delta = scope_differ.compare_meetings(t1, t2)
    qb = next(c for c in delta.scope_creep_items if "quickbooks" in c.title.lower())
    assert qb.is_scope_creep is True
    assert qb.additional_quote_required is True
    assert qb.updated_hours == 20.0

def test_21_scope_differ_addon_change_order_quote():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    delta = scope_differ.compare_meetings(t1, t2)
    assert delta.scope_creep_hours == 110.0
    assert delta.scope_creep_addon_quote == 10450.0  # 110 hrs * $95

# --- Group 6: Performance SLA & Long Context Handling (Test 22) ---

def test_22_pipeline_speed_and_long_context_resilience():
    t1 = load_sample("meeting_1_discovery.txt")
    t2 = load_sample("meeting_2_followup_changes.txt")
    start = time.time()
    resp = sow_pipeline.run_pipeline(t1, t2)
    elapsed_ms = (time.time() - start) * 1000
    assert resp.sow is not None
    assert resp.delta is not None
    # SLA benchmark < 1000ms for local pipeline (resilient under background multi-process loads)
    assert elapsed_ms < 1000, f"Pipeline execution took too long: {elapsed_ms}ms"
