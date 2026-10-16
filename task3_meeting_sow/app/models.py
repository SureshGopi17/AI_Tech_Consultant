"""
Pydantic data models for Task 3: Meeting to Scope of Work.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class RequirementItem(BaseModel):
    id: str
    title: str
    raw_statement: str
    category: str  # Search, Billing, Member Management, Design, Integration, Mobile
    is_native_setting: bool = False
    native_setting_path: Optional[str] = None
    kb_citation_title: Optional[str] = None
    kb_citation_url: Optional[str] = None
    resolution_type: str = "NATIVE_SETTING"  # NATIVE_SETTING vs CUSTOM_DEV
    notes: str = ""

class DeveloperTask(BaseModel):
    id: str
    requirement_id: str
    task_name: str
    description: str
    dev_type: str  # Frontend, Backend, API/Webhook, Configuration, QA
    estimated_hours: float
    hourly_rate: float = 95.0
    cost: float = 0.0

class SOWAnalysis(BaseModel):
    meeting_title: str
    client_name: str
    company_name: str
    business_objective: str
    requirements: List[RequirementItem]
    native_count: int = 0
    custom_count: int = 0
    estimated_savings_from_native: float = 0.0

class TaskBreakdown(BaseModel):
    tasks: List[DeveloperTask]
    total_hours: float
    total_cost: float
    qa_buffer_hours: float
    project_management_hours: float

class ProposalDocument(BaseModel):
    proposal_id: str
    title: str
    client_name: str
    company_name: str
    executive_summary: str
    scope_overview: str
    native_features_utilized: List[str]
    custom_deliverables: List[str]
    timeline_weeks: str
    total_hours: float
    total_investment: float
    approved_by_human: bool = False
    approved_at: Optional[str] = None

class ScopeDeltaItem(BaseModel):
    id: str
    title: str
    status: str  # MODIFIED, DROPPED, UNCHANGED, NEW_IN_SCOPE, SCOPE_CREEP
    change_description: str
    original_hours: float = 0.0
    updated_hours: float = 0.0
    is_scope_creep: bool = False
    additional_quote_required: bool = False
    extra_cost: float = 0.0

class ScopeDeltaReport(BaseModel):
    baseline_meeting: str
    updated_meeting: str
    modified_items: List[ScopeDeltaItem]
    dropped_items: List[ScopeDeltaItem]
    unchanged_items: List[ScopeDeltaItem]
    scope_creep_items: List[ScopeDeltaItem]
    total_baseline_hours: float
    total_updated_hours: float
    scope_creep_hours: float
    scope_creep_addon_quote: float
    summary: str

class PipelineRunResponse(BaseModel):
    sow: SOWAnalysis
    tasks: TaskBreakdown
    proposal: ProposalDocument
    delta: Optional[ScopeDeltaReport] = None
    latency_ms: float = 0.0
