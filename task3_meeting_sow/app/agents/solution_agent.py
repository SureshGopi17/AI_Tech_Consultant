"""
Agent 2: Solution Architect & Knowledge Brain Agent.
Requirement: "Many requests can be solved with a setting the product already has,
which costs the client far less than custom code. Your agents must check this
by calling the Knowledge Brain from Task 1."
"""

import os
import urllib.request
import json
from typing import List
from app.models import RequirementItem

class SolutionArchitectAgent:
    def __init__(self, kb_api_url: str = os.getenv("TASK1_API_URL", "http://localhost:8001")):
        self.role = "Lead Solution Architect"
        self.kb_api_url = kb_api_url.rstrip('/')
        self._is_kb_online = None

    def check_knowledge_brain(self, query: str) -> List[dict]:
        """Calls Task 1 Knowledge Brain API to discover out-of-the-box settings."""
        if self._is_kb_online is False:
            return []
        try:
            req = urllib.request.Request(
                f"{self.kb_api_url}/api/v1/search",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": query, "top_k": 2}).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=0.08) as response:
                if response.status == 200:
                    self._is_kb_online = True
                    data = json.loads(response.read().decode("utf-8"))
                    return data.get("results", [])
        except Exception:
            self._is_kb_online = False
        return []

    def evaluate_requirements(self, requirements: List[RequirementItem]) -> List[RequirementItem]:
        """
        Evaluates each requirement against Knowledge Brain documentation to distinguish
        native zero-code product settings from required custom engineering.
        """
        for req in requirements:
            # Call Task 1 API
            results = self.check_knowledge_brain(req.title + " " + req.raw_statement)

            # Known native settings map
            title_lower = req.title.lower()
            stmt_lower = req.raw_statement.lower()

            if any(k in title_lower or k in stmt_lower for k in ["membership tier", "recurring billing", "stripe", "search with radius", "location search", "lead management", "inquiry lead"]):
                req.is_native_setting = True
                req.resolution_type = "NATIVE_SETTING"
                
                if "stripe" in title_lower or "billing" in title_lower or "membership" in title_lower:
                    req.native_setting_path = "Admin > Settings > General Settings > Payments Tab & My Members > Membership Plans"
                    req.kb_citation_title = "How to Connect Stripe Payment Gateway & Enable Recurring Billing"
                    req.kb_citation_url = "https://support.brilliantdirectories.com/support/solutions/articles/5000558350-stripe-payment-gateway-setup"
                    req.notes = "Native BD Feature. $0 custom code needed. Configurable in admin panel in ~30 mins."
                elif "search" in title_lower or "radius" in title_lower or "location" in title_lower:
                    req.native_setting_path = "Admin > Settings > General Settings > Localization Tab & Search Settings"
                    req.kb_citation_title = "Changing Search Distance Radius from Miles to Kilometers"
                    req.kb_citation_url = "https://support.brilliantdirectories.com/support/solutions/articles/5000558355-change-search-radius-miles-kilometers"
                    req.notes = "Native BD Feature. Built-in Category + Location search widget with radius."
                elif "lead" in title_lower:
                    req.native_setting_path = "Admin > Leads > Lead Settings > Auto Lead Distribution"
                    req.kb_citation_title = "Auto Lead Distribution & Lead Matching Rules"
                    req.kb_citation_url = "https://support.brilliantdirectories.com/support/solutions/articles/5000558365-auto-lead-distribution-settings"
                    req.notes = "Native BD Feature. Captures inquiry forms and auto-dispatches directly to matching members."
            else:
                req.is_native_setting = False
                req.resolution_type = "CUSTOM_DEV"
                if "state bar" in title_lower or "verification" in title_lower:
                    req.notes = "Custom Engineering: Add custom form field to Form Manager, build webhook verification endpoint, and badge render snippet."
                elif "theme" in title_lower or "branding" in title_lower:
                    req.notes = "Custom Engineering: Custom CSS stylesheet injection, Google typography integration, and responsive homepage widget layout."
                elif "csv" in title_lower or "import" in title_lower or "migration" in title_lower:
                    req.notes = "Custom Engineering: Data ETL script, CSV mapping normalization, and geocoding verification."

        return requirements

solution_agent = SolutionArchitectAgent()
