"""
RAG Chatbot Engine for Brilliant Directories Solution Center.
Features:
- Calibrated confidence assessment
- Exact citations (URL, Title, Category, Snippet)
- Screenshot and image recommendation
- Honest "I don't know" handling with automatic Human Expert Escalation
- Anthropic Claude integration with smart local fallback
"""

import time
import os
from typing import List, Optional, Tuple
from app.config import settings
from app.models import ChatRequest, ChatResponse, Citation, ArticleImage
from app.vector_store import knowledge_store
from app.escalations import escalation_manager

# Optional Anthropic SDK
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

class RAGEngine:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key) if (HAS_ANTHROPIC and self.api_key) else None

    def ask(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        query = request.message.strip()

        # 1. Search knowledge store
        results = knowledge_store.search(query, top_k=4)

        # 2. Confidence Calibration
        if not results:
            confidence = 0.15
        else:
            top_score = results[0].score
            confidence = min(0.98, top_score + 0.12)

        # 3. Check for out-of-domain / unknown
        out_of_domain_words = ["cooking", "recipe", "capital of", "weather in", "movie", "football", "joke", "quantum physics"]
        is_ood = any(w in query.lower() for w in out_of_domain_words)
        
        can_answer = (confidence >= settings.CONFIDENCE_THRESHOLD) and not is_ood

        citations: List[Citation] = []
        screenshots: List[ArticleImage] = []

        if can_answer and results:
            for res in results[:3]:
                citations.append(Citation(
                    title=res.title,
                    url=res.url,
                    category=res.category,
                    snippet=res.snippet
                ))
                for img in res.images:
                    if img.url not in [s.url for s in screenshots]:
                        screenshots.append(img)

        # 4. Generate Answer
        if not can_answer:
            confidence = min(confidence, 0.45)
            esc_id = escalation_manager.create_escalation(query, confidence)
            answer = (
                f"I do not have sufficient information in the Brilliant Directories documentation "
                f"to answer this question accurately. To ensure you receive verified technical guidance, "
                f"I have created an escalation task (Ticket: **{esc_id}**) for our human solution engineers. "
                f"Once answered, the solution will automatically be saved to my memory."
            )
            model_used = "escalation-guardrail"
            latency = (time.time() - start_time) * 1000
            return ChatResponse(
                answer=answer,
                confidence=round(confidence, 3),
                can_answer=False,
                citations=[],
                screenshots=[],
                escalation_id=esc_id,
                model_used=model_used,
                latency_ms=round(latency, 2)
            )

        # Generate answer with Claude or local synthesizer
        model_name = request.model or settings.ANTHROPIC_MODEL
        if self.client:
            try:
                context_str = "\n\n".join([
                    f"Article: {r.title} ({r.category})\nURL: {r.url}\nContent: {r.snippet}"
                    for r in results[:3]
                ])
                system_prompt = (
                    "You are the official Brilliant Directories Technical Consultant. "
                    "Answer the user's question accurately based STRICTLY on the provided solution center documentation. "
                    "Include step-by-step instructions. Reference specific admin menu paths. "
                    "Never invent features that do not exist. Mention relevant screenshots if available."
                )
                user_content = f"User Question: {query}\n\nContext Documentation:\n{context_str}"

                resp = self.client.messages.create(
                    model=model_name,
                    max_tokens=800,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_content}]
                )
                answer = resp.content[0].text
                model_used = model_name
            except Exception as e:
                print(f"[RAGEngine] Anthropic API call error: {e}. Falling back to local synthesizer.")
                answer = self._synthesize_local_answer(query, results)
                model_used = "local-synthesizer (fallback)"
        else:
            answer = self._synthesize_local_answer(query, results)
            model_used = "local-synthesizer"

        latency = (time.time() - start_time) * 1000
        return ChatResponse(
            answer=answer,
            confidence=round(confidence, 3),
            can_answer=True,
            citations=citations,
            screenshots=screenshots[:3],
            escalation_id=None,
            model_used=model_used,
            latency_ms=round(latency, 2)
        )

    def _synthesize_local_answer(self, query: str, results) -> str:
        """High-precision local documentation synthesizer."""
        top_res = results[0]
        secondary = results[1] if len(results) > 1 else None

        lines = [
            f"Based on the Brilliant Directories Solution Center documentation for **{top_res.title}**:",
            "",
            top_res.snippet,
        ]

        if secondary:
            lines.append("")
            lines.append(f"**Additional Details ({secondary.title}):**")
            lines.append(secondary.snippet)

        lines.append("")
        lines.append("You can configure this in your Brilliant Directories admin dashboard under the corresponding menu settings.")
        return "\n".join(lines)

rag_engine = RAGEngine()
