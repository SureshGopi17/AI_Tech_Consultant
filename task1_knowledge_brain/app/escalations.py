"""
Human-in-the-Loop Escalation Manager.
When the chatbot cannot answer, it logs an escalation ticket.
When a human expert answers, that verified answer flows back into memory.
"""

import os
import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone

from app.config import settings
from app.models import EscalationItem

class EscalationManager:
    def __init__(self, filepath: str = settings.ESCALATIONS_FILE):
        self.filepath = filepath
        self.escalations: List[EscalationItem] = []
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.escalations = [EscalationItem(**item) for item in data]
            except Exception as e:
                print(f"[Escalations] Error loading file: {e}")

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([item.model_dump() if hasattr(item, "model_dump") else item.dict() for item in self.escalations], f, indent=2)

    def create_escalation(self, question: str, confidence: float) -> str:
        """Creates a pending escalation task for a human expert."""
        # Check if question is already in pending queue
        for esc in self.escalations:
            if esc.question.lower() == question.lower() and esc.status == "PENDING":
                return esc.id

        esc_id = f"ESC-{uuid.uuid4().hex[:6].upper()}"
        item = EscalationItem(
            id=esc_id,
            question=question,
            confidence=round(confidence, 3),
            created_at=datetime.now(timezone.utc).isoformat(),
            status="PENDING"
        )
        self.escalations.insert(0, item)
        self.save()
        print(f"[Escalations] Created new expert escalation task {esc_id} for: '{question[:50]}'")
        return esc_id

    def list_escalations(self, status: Optional[str] = None) -> List[EscalationItem]:
        if status:
            return [e for e in self.escalations if e.status.upper() == status.upper()]
        return self.escalations

    def resolve_escalation(self, esc_id: str, expert_answer: str, resolved_by: str = "Human Expert") -> Optional[EscalationItem]:
        """Resolves an escalation and marks it completed."""
        for esc in self.escalations:
            if esc.id == esc_id:
                esc.status = "RESOLVED"
                esc.expert_answer = expert_answer
                esc.resolved_at = datetime.now(timezone.utc).isoformat()
                esc.resolved_by = resolved_by
                self.save()
                return esc
        return None

escalation_manager = EscalationManager()
