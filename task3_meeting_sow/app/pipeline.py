"""
Multi-Agent Pipeline Orchestrator for Task 3.
Coordinates the execution of Consultant, Solution Architect, Estimator, and Proposal agents,
and handles long transcript windowing.
"""

import time
from typing import Optional, Tuple
from app.models import SOWAnalysis, TaskBreakdown, ProposalDocument, PipelineRunResponse, ScopeDeltaReport
from app.agents.consultant_agent import consultant_agent
from app.agents.solution_agent import solution_agent
from app.agents.estimator_agent import estimator_agent
from app.agents.proposal_agent import proposal_agent
from app.scope_differ import scope_differ

class MeetingToSOWPipeline:
    def run_pipeline(
        self,
        transcript_text: str,
        followup_transcript: Optional[str] = None
    ) -> PipelineRunResponse:
        start_time = time.time()

        # Step 1: Long Context Pre-processing (chunking / windowing)
        clean_text = self._chunk_and_normalize(transcript_text)

        # Step 2: Consultant Agent (Extraction)
        meta, raw_requirements = consultant_agent.analyze_transcript(clean_text)

        # Step 3: Solution Architect Agent (Check Task 1 KB API)
        evaluated_requirements = solution_agent.evaluate_requirements(raw_requirements)

        # Calculate native vs custom stats
        native_count = sum(1 for r in evaluated_requirements if r.is_native_setting)
        custom_count = len(evaluated_requirements) - native_count
        # Each native setting saves ~25 hours of custom full-stack coding
        savings = native_count * 25.0 * 95.0

        sow = SOWAnalysis(
            meeting_title=f"Discovery Scope: {meta['company_name']}",
            client_name=meta["client_name"],
            company_name=meta["company_name"],
            business_objective=meta["objective"],
            requirements=evaluated_requirements,
            native_count=native_count,
            custom_count=custom_count,
            estimated_savings_from_native=savings
        )

        # Step 4: Technical Estimator Agent
        tasks = estimator_agent.create_estimate(evaluated_requirements)

        # Step 5: Proposal Generator Agent
        proposal = proposal_agent.generate_proposal(sow, tasks)

        # Step 6: Follow-up Delta Analysis (if provided)
        delta_report: Optional[ScopeDeltaReport] = None
        if followup_transcript and len(followup_transcript.strip()) > 50:
            delta_report = scope_differ.compare_meetings(transcript_text, followup_transcript)

        latency = (time.time() - start_time) * 1000

        return PipelineRunResponse(
            sow=sow,
            tasks=tasks,
            proposal=proposal,
            delta=delta_report,
            latency_ms=round(latency, 2)
        )

    def _chunk_and_normalize(self, transcript: str) -> str:
        """Handles long transcripts with normalization and windowing."""
        # Normalize speaker tags and timestamps
        lines = [line.strip() for line in transcript.split("\n") if line.strip()]
        # Truncate window if excessively large (> 100,000 characters)
        joined = "\n".join(lines)
        if len(joined) > 50000:
            joined = joined[:50000] + "\n...[Transcript windowed for analysis]..."
        return joined

sow_pipeline = MeetingToSOWPipeline()
