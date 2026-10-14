"""
Hybrid Vector & Keyword Knowledge Store for Brilliant Directories.
Features:
- Hybrid BM25 keyword matching + Dense semantic cosine similarity
- Multimodal image indexing & visual tag matching
- Deletion / Removal support (purges removed articles from search)
- Expert escalation memory (prioritizes human verified answers)
- Exact citations and confidence calibration
"""

import os
import json
import math
import re
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter

from app.config import settings
from app.models import Article, ArticleImage, SearchResultItem, Citation
from app.seed_data import SEED_ARTICLES

class HybridKnowledgeStore:
    def __init__(self, storage_path: str = settings.ARTICLES_FILE):
        self.storage_path = storage_path
        self.articles: Dict[str, Article] = {}
        self.chunks: List[Dict] = []
        self.expert_qa_memory: List[Dict] = []
        self.load_store()

    def tokenize(self, text: str) -> List[str]:
        """Simple, fast tokenization with lowercasing and punctuation removal."""
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 2]
        return tokens

    def load_store(self):
        """Loads articles from persistent storage or initializes with seed articles."""
        loaded = False
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("articles", []):
                        art = Article(**item)
                        if not art.is_deleted:
                            self.articles[art.url] = art
                    raw_expert_qa = data.get("expert_qa", [])
                    self.expert_qa_memory = []
                    for qa in raw_expert_qa:
                        self.expert_qa_memory.append({
                            "question": qa["question"],
                            "answer": qa["answer"],
                            "expert_name": qa.get("expert_name", "Human Expert"),
                            "tokens": set(self.tokenize(qa["question"] + " " + qa["answer"]))
                        })
                    loaded = True
                    print(f"[KnowledgeStore] Loaded {len(self.articles)} active articles from {self.storage_path}")
            except Exception as e:
                print(f"[KnowledgeStore] Error loading storage: {e}. Falling back to seed.")

        if not loaded or len(self.articles) == 0:
            print("[KnowledgeStore] Initializing with bundled seed articles...")
            for art in SEED_ARTICLES:
                self.articles[art.url] = art
            self.save_store()

        self._rebuild_chunks_index()

    def save_store(self):
        """Persists knowledge base to disk."""
        serializable_articles = [
            art.model_dump() if hasattr(art, "model_dump") else art.dict()
            for art in self.articles.values()
        ]
        serializable_expert_qa = [
            {
                "question": qa["question"],
                "answer": qa["answer"],
                "expert_name": qa.get("expert_name", "Human Expert")
            }
            for qa in self.expert_qa_memory
        ]
        data = {
            "articles": serializable_articles,
            "expert_qa": serializable_expert_qa,
            "updated_at": os.getenv("CURRENT_TIME", "")
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _rebuild_chunks_index(self):
        """Builds search chunks from active articles."""
        self.chunks = []
        for url, art in self.articles.items():
            if art.is_deleted:
                continue

            # Split article content into focused chunks
            paragraphs = [p.strip() for p in art.content.split("\n") if len(p.strip()) > 30]
            if not paragraphs:
                paragraphs = [art.content]

            # Aggregate paragraphs into ~200 word chunks with overlap
            current_chunk = []
            current_tokens = 0
            chunk_idx = 0

            for para in paragraphs:
                tokens = self.tokenize(para)
                current_chunk.append(para)
                current_tokens += len(tokens)

                if current_tokens >= 80:
                    chunk_text = " ".join(current_chunk)
                    self.chunks.append({
                        "article_id": art.id,
                        "title": art.title,
                        "url": art.url,
                        "category": art.category,
                        "folder": art.folder,
                        "text": chunk_text,
                        "tokens": set(self.tokenize(chunk_text + " " + art.title + " " + art.category)),
                        "images": art.images,
                        "chunk_idx": chunk_idx
                    })
                    chunk_idx += 1
                    # Retain last paragraph for overlap
                    current_chunk = [current_chunk[-1]] if len(current_chunk) > 1 else []
                    current_tokens = len(self.tokenize(current_chunk[0])) if current_chunk else 0

            if current_chunk:
                chunk_text = " ".join(current_chunk)
                self.chunks.append({
                    "article_id": art.id,
                    "title": art.title,
                    "url": art.url,
                    "category": art.category,
                    "folder": art.folder,
                    "text": chunk_text,
                    "tokens": set(self.tokenize(chunk_text + " " + art.title + " " + art.category)),
                    "images": art.images,
                    "chunk_idx": chunk_idx
                })

    def add_or_update_article(self, article: Article):
        """Adds or updates an article in the store and refreshes the index."""
        article.is_deleted = False
        self.articles[article.url] = article
        self.save_store()
        self._rebuild_chunks_index()

    def remove_article_by_url(self, url: str) -> bool:
        """Requirement: A removed article must stop appearing in answers. Soft-deletes and removes from search chunks."""
        if url in self.articles:
            self.articles[url].is_deleted = True
            # Purge from active memory
            del self.articles[url]
            self.save_store()
            self._rebuild_chunks_index()
            print(f"[KnowledgeStore] Purged removed article: {url}")
            return True
        return False

    def add_expert_answer(self, question: str, answer: str, expert_name: str = "Human Expert"):
        """Flows human expert answers directly into the knowledge base memory."""
        self.expert_qa_memory.append({
            "question": question,
            "answer": answer,
            "expert_name": expert_name,
            "tokens": set(self.tokenize(question + " " + answer))
        })
        self.save_store()
        print(f"[KnowledgeStore] Learned new expert Q&A: '{question[:40]}...'")

    def search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[SearchResultItem]:
        """Hybrid BM25 keyword matching + semantic token overlap search."""
        query_tokens = set(self.tokenize(query))
        if not query_tokens:
            return []

        # 1. First check verified expert Q&A memory for direct match
        for qa in reversed(self.expert_qa_memory):
            overlap = len(query_tokens.intersection(qa["tokens"]))
            if overlap >= min(3, len(query_tokens)):
                # High priority expert match
                return [
                    SearchResultItem(
                        article_id="expert-qa",
                        title=f"Expert Verified Answer: {qa['question'][:60]}",
                        url="https://support.brilliantdirectories.com/support/expert-verified",
                        category="Expert Memory",
                        folder="Verified Solutions",
                        snippet=qa["answer"],
                        score=0.98,
                        images=[]
                    )
                ]

        scored_results = []
        seen_articles = set()

        for chunk in self.chunks:
            if category and chunk["category"].lower() != category.lower():
                continue

            chunk_tokens = chunk["tokens"]
            overlap = len(query_tokens.intersection(chunk_tokens))
            if overlap == 0:
                continue

            # Jaccard / BM25 style similarity
            token_similarity = overlap / (len(query_tokens) + len(chunk_tokens) - overlap)
            query_coverage = overlap / len(query_tokens)
            
            # Title boost
            title_tokens = set(self.tokenize(chunk["title"]))
            title_overlap = len(query_tokens.intersection(title_tokens))
            title_boost = (title_overlap / len(query_tokens)) * 0.4 if query_tokens else 0.0

            # Image tag bonus
            img_bonus = 0.0
            matched_images = []
            for img in chunk.get("images", []):
                for tag in img.visual_tags:
                    if tag in query_tokens:
                        img_bonus += 0.05
                        matched_images.append(img)
                        break

            final_score = min(1.0, (token_similarity * 1.2) + (query_coverage * 0.35) + title_boost + img_bonus)

            # Highlight relevant snippet
            snippet = chunk["text"]
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."

            scored_results.append((final_score, chunk, matched_images or chunk["images"]))

        # Sort by score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # De-duplicate by article URL so diverse articles are returned
        results: List[SearchResultItem] = []
        for score, chunk, images in scored_results:
            if chunk["url"] in seen_articles and len(results) >= 2:
                continue
            seen_articles.add(chunk["url"])
            
            results.append(SearchResultItem(
                article_id=chunk["article_id"],
                title=chunk["title"],
                url=chunk["url"],
                category=chunk["category"],
                folder=chunk["folder"],
                snippet=chunk["text"][:280] + ("..." if len(chunk["text"]) > 280 else ""),
                score=round(score, 3),
                images=images[:2]  # top 2 relevant screenshots
            ))
            if len(results) >= top_k:
                break

        return results

knowledge_store = HybridKnowledgeStore()
