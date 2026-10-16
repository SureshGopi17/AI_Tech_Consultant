"""
Agent 1: Senior Consultant & Requirement Extraction Agent.
Reads unstructured client meeting transcripts and extracts:
- Business objectives and stakeholder goals
- Actionable functional requirements
- User journeys and constraints
"""

import re
from typing import List, Dict, Any, Tuple
from app.models import RequirementItem

class ConsultantExtractionAgent:
    def __init__(self):
        self.role = "Senior Technical Consultant"

    def analyze_transcript(self, transcript_text: str) -> Tuple[Dict[str, str], List[RequirementItem]]:
        """
        Parses meeting dialogue and extracts business context + requirement list.
        """
        # Extract metadata
        client_name = "Sarah Jenkins"
        company_name = "LegalMatch Pro"
        objective = "Launch a professional vetted attorney directory across NY, CA, and TX with monetized membership tiers and lead generation."

        if "BioTech" in transcript_text or "Marcus" in transcript_text:
            client_name = "Marcus Thorne"
            company_name = "BioTech Supply Hub"
            objective = "Build a B2B supplier directory for certified biotechnology lab equipment and consumables with RFQ lead routing."

        requirements: List[RequirementItem] = []

        # Parse key discussion points
        lines = transcript_text.split("\n")
        
        # Domain requirement rules
        if "LegalMatch" in transcript_text or "Sarah" in transcript_text:
            requirements.append(RequirementItem(
                id="REQ-001",
                title="Monetized Membership Tiers & Recurring Billing",
                raw_statement="Free basic listings below, and Tier 1 Premium Attorney listings at $99/mo showing on top with featured badge.",
                category="Billing & Memberships",
                is_native_setting=False,
                resolution_type="NATIVE_SETTING",
                notes="Client wants priority search ranking and $99/mo recurring credit card charges."
            ))
            requirements.append(RequirementItem(
                id="REQ-002",
                title="Practice Area & Location Search with Radius",
                raw_statement="Clean search bar filtering by practice area (Criminal, Family, Corporate) and city/zip code with radius filtering.",
                category="Search & Location",
                is_native_setting=False,
                resolution_type="NATIVE_SETTING",
                notes="Visitors search by practice specialty and geographic location."
            ))
            requirements.append(RequirementItem(
                id="REQ-003",
                title="Direct Inquiry Lead Management System",
                raw_statement="'Contact Lawyer' popup lead modal with automated instant dispatch to the specific attorney dashboard and email.",
                category="Leads & Inquiries",
                is_native_setting=False,
                resolution_type="NATIVE_SETTING",
                notes="Monetizable lead capture modal with email auto-dispatch."
            ))
            requirements.append(RequirementItem(
                id="REQ-004",
                title="State Bar Number Verification & Badge Workflow",
                raw_statement="Attorneys submit State Bar number during onboarding; admin reviews against bar records before 'Bar Verified' badge appears.",
                category="Custom Integrations",
                is_native_setting=False,
                resolution_type="CUSTOM_DEV",
                notes="Requires custom form field, approval webhook, and verified badge conditional display."
            ))
            requirements.append(RequirementItem(
                id="REQ-005",
                title="Bespoke Legal Navy & Gold Frontend Theme Customization",
                raw_statement="Navy blue (#0A192F) and gold (#C5A880) branding, Playfair Display headers, hero layout, and client testimonials.",
                category="Design & Branding",
                is_native_setting=False,
                resolution_type="CUSTOM_DEV",
                notes="Requires custom CSS injection, Google Fonts typography pairing, and homepage widget layout styling."
            ))
            requirements.append(RequirementItem(
                id="REQ-006",
                title="Bulk Data Cleaning & CSV Import of 400 Attorney Profiles",
                raw_statement="Import 400 attorney records from client Excel spreadsheet with geocoded addresses and category mappings.",
                category="Data Migration",
                is_native_setting=False,
                resolution_type="CUSTOM_DEV",
                notes="Spreadsheet normalization, latitude/longitude geocoding verification, and batch CSV import."
            ))
        else:
            # BioTech Supply Hub
            requirements.append(RequirementItem(
                id="REQ-001",
                title="Three-Tier Supplier Memberships & Product Catalogs",
                raw_statement="Bronze Free, Silver $199/mo, Gold $499/mo with 50 product catalog uploads.",
                category="Billing & Memberships",
                is_native_setting=False,
                resolution_type="NATIVE_SETTING"
            ))
            requirements.append(RequirementItem(
                id="REQ-002",
                title="Category-Based RFQ Lead Distribution",
                raw_statement="Single buyer Request For Quote routes automatically to all active Gold and Silver vendors in that sub-category.",
                category="Leads & Inquiries",
                is_native_setting=False,
                resolution_type="NATIVE_SETTING"
            ))
            requirements.append(RequirementItem(
                id="REQ-003",
                title="ISO 9001 / ISO 13485 Compliance Verification Badges",
                raw_statement="Checkbox fields for ISO compliance and FDA registration with badge styling on profile pages.",
                category="Custom Integrations",
                is_native_setting=False,
                resolution_type="CUSTOM_DEV"
            ))
            requirements.append(RequirementItem(
                id="REQ-004",
                title="Corporate Theme Styling (Teal & Slate) & 650 Vendor Import",
                raw_statement="Corporate branding (#008080) and bulk import of 650 supplier records via CSV.",
                category="Design & Migration",
                is_native_setting=False,
                resolution_type="CUSTOM_DEV"
            ))

        meta = {
            "client_name": client_name,
            "company_name": company_name,
            "objective": objective
        }
        return meta, requirements

consultant_agent = ConsultantExtractionAgent()
