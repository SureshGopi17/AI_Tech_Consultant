"""
Agent 4: Client Proposal Generator Agent.
Compiles a polished, client-ready proposal with executive summary,
native architecture savings, custom deliverables, milestone timeline, and investment.
Requirement: "Nothing reaches the client until a human approves it."
"""

import uuid
from typing import List, Dict
from app.models import SOWAnalysis, TaskBreakdown, ProposalDocument

class ProposalGeneratorAgent:
    def __init__(self):
        self.role = "Senior Managing Consultant"

    def generate_proposal(self, sow: SOWAnalysis, tasks: TaskBreakdown) -> ProposalDocument:
        proposal_id = f"PROP-{uuid.uuid4().hex[:6].upper()}"

        native_features = [
            f"{r.title} (Utilizes native setting: {r.native_setting_path})"
            for r in sow.requirements if r.is_native_setting
        ]

        custom_deliverables = [
            f"{t.task_name} ({t.estimated_hours} hrs) - {t.description}"
            for t in tasks.tasks if t.dev_type != "Configuration"
        ]

        exec_summary = (
            f"BusinessLabs is pleased to submit this formal proposal to {sow.client_name} and {sow.company_name}. "
            f"Our strategy maximizes your return on investment by leveraging out-of-the-box Brilliant Directories "
            f"core features for memberships, Stripe recurring billing, and auto-lead distribution—saving you an estimated "
            f"${sow.estimated_savings_from_native:,.2f} in unnecessary custom software development. "
            f"Our engineering efforts focus strictly on high-value bespoke capabilities: tailored branding, "
            f"custom credential verification workflows, and turnkey data migration."
        )

        scope_overview = (
            f"This project encompasses the full setup, styling, and deployment of {sow.company_name}. "
            f"Phase 1 delivery includes {len(sow.requirements)} total functional requirements ({sow.native_count} native, "
            f"{sow.custom_count} custom development tasks). Total estimated engineering scope is {tasks.total_hours} hours."
        )

        timeline_weeks = "3 to 4 Weeks from kickoff to staging launch"

        return ProposalDocument(
            proposal_id=proposal_id,
            title=f"Technical Implementation & Launch Proposal for {sow.company_name}",
            client_name=sow.client_name,
            company_name=sow.company_name,
            executive_summary=exec_summary,
            scope_overview=scope_overview,
            native_features_utilized=native_features,
            custom_deliverables=custom_deliverables,
            timeline_weeks=timeline_weeks,
            total_hours=tasks.total_hours,
            total_investment=tasks.total_cost,
            approved_by_human=False,
            approved_at=None
        )

proposal_agent = ProposalGeneratorAgent()
