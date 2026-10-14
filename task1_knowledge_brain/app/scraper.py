"""
Polite Web Scraper for Brilliant Directories Solution Center.
Features:
- Polite rate-limiting & batching
- Checkpoint persistence & resume capability
- HTML text extraction (breadcrumbs, title, content)
- Multimodal image extraction (screenshots, captions, visual tags)
- Content hashing for daily change detection
"""

import os
import json
import time
import hashlib
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
import urllib.request
import urllib.error
import ssl

from app.config import settings
from app.models import Article, ArticleImage

class PoliteHelpCenterScraper:
    def __init__(self, sitemap_url: str = settings.SITEMAP_URL):
        self.sitemap_url = sitemap_url
        self.checkpoint_file = settings.CHECKPOINT_FILE
        self.articles_file = settings.ARTICLES_FILE
        self.ssl_context = ssl.create_default_context()
        self.headers = {
            "User-Agent": "AITechConsultantKnowledgeBot/1.0 (+https://businesslabs.ai; contact@businesslabs.ai)"
        }

    def load_checkpoint(self) -> Dict:
        """Loads scraping progress from checkpoint file to allow seamless resume."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Scraper] Warning: failed to read checkpoint: {e}")
        return {"completed_urls": {}, "last_scraped_index": 0, "total_urls": 0}

    def save_checkpoint(self, checkpoint_data: Dict):
        """Persists checkpoint to disk."""
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2)

    def fetch_sitemap_urls(self) -> List[Dict[str, str]]:
        """Parses the sitemap.xml and returns all article URLs with their lastmod dates."""
        print(f"[Scraper] Fetching sitemap from {self.sitemap_url}...")
        try:
            req = urllib.request.Request(self.sitemap_url, headers=self.headers)
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=15) as resp:
                xml_data = resp.read()
            
            root = ET.fromstring(xml_data)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            items = []
            for url_elem in root.findall('ns:url', namespace):
                loc = url_elem.find('ns:loc', namespace)
                lastmod = url_elem.find('ns:lastmod', namespace)
                if loc is not None and loc.text:
                    url_text = loc.text.strip()
                    # Filter for solution articles
                    if "/solutions/articles/" in url_text:
                        lastmod_text = lastmod.text.strip() if lastmod is not None and lastmod.text else ""
                        items.append({"url": url_text, "lastmod": lastmod_text})
            
            print(f"[Scraper] Found {len(items)} article URLs in sitemap.")
            return items
        except Exception as e:
            print(f"[Scraper] Error fetching sitemap: {e}")
            return []

    def fetch_page_html(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Politely fetches an HTML page with exponential backoff & jitter."""
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, context=self.ssl_context, timeout=12) as response:
                    if response.status == 200:
                        return response.read().decode("utf-8", errors="ignore")
            except urllib.error.HTTPError as he:
                if he.code == 429:
                    wait_time = (2 ** attempt) * 2
                    print(f"[Scraper] Rate limited (429) on {url}. Backing off for {wait_time}s...")
                    time.sleep(wait_time)
                elif he.code == 404:
                    print(f"[Scraper] Article not found (404): {url}")
                    return None
                else:
                    time.sleep(1)
            except Exception as e:
                time.sleep(1 + attempt * 0.5)
        return None

    def clean_html_to_text(self, html_snippet: str) -> str:
        """Strips HTML tags and normalizes whitespace."""
        text = re.sub(r'<script.*?</script>', '', html_snippet, flags=re.DOTALL | re.I)
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_article(self, url: str, html: str, lastmod: str = "") -> Article:
        """Extracts structured Article metadata, content, and screenshots from HTML."""
        # 1. Title
        title_match = re.search(r'<title>(.*?)</title>', html, re.I | re.DOTALL)
        raw_title = title_match.group(1).strip() if title_match else "Brilliant Directories Article"
        # Clean title branding suffixes
        title = re.sub(r'\s*-\s*Brilliant Directories.*$', '', raw_title, flags=re.I).strip()
        if not title:
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.DOTALL)
            title = self.clean_html_to_text(h1_match.group(1)) if h1_match else "Documentation Article"

        # 2. Breadcrumbs / Category / Folder
        breadcrumb_matches = re.findall(r'<li[^>]*class=[\'"][^\'"]*breadcrumb[^\'"]*[\'"][^>]*>(.*?)</li>', html, re.I | re.DOTALL)
        category = "General"
        folder = "General"
        if breadcrumb_matches and len(breadcrumb_matches) >= 2:
            crumbs = [self.clean_html_to_text(c) for c in breadcrumb_matches]
            crumbs = [c for c in crumbs if c and c.lower() not in ["home", "solutions"]]
            if len(crumbs) >= 1:
                category = crumbs[0]
            if len(crumbs) >= 2:
                folder = crumbs[1]

        # 3. Main Article Body
        body_match = re.search(r'<(div|article)[^>]+class=[\'"][^\'"]*(article-body|content-body|body-content)[^\'"]*[\'"][^>]*>(.*?)</\1>', html, re.I | re.DOTALL)
        body_html = body_match.group(3) if body_match else html

        # 4. Extract Images / Screenshots
        images: List[ArticleImage] = []
        img_tags = re.findall(r'<img\s+([^>]+)>', body_html, re.I)
        for tag_attrs in img_tags:
            src_m = re.search(r'src=[\'"]([^\'"]+)[\'"]', tag_attrs, re.I)
            alt_m = re.search(r'alt=[\'"]([^\'"]*)[\'"]', tag_attrs, re.I)
            if src_m:
                src = src_m.group(1).strip()
                alt = alt_m.group(1).strip() if alt_m else ""
                
                # Filter out small tracking pixels, badges or icons
                if any(ignored in src.lower() for ignored in ["favicon", "logo", "icon", "tracker", "1x1"]):
                    continue
                
                # Generate visual tags based on alt, src and context
                visual_tags = []
                for kw in ["settings", "admin", "dashboard", "form", "stripe", "billing", "search", "category", "lead", "member", "menu", "toggle", "code"]:
                    if kw in alt.lower() or kw in src.lower() or kw in title.lower():
                        visual_tags.append(kw)
                
                caption = alt if alt else f"Screenshot from {title}"
                images.append(ArticleImage(
                    url=src,
                    caption=caption,
                    alt_text=alt,
                    section=category,
                    visual_tags=visual_tags
                ))

        # 5. Clean text content
        clean_text = self.clean_html_to_text(body_html)
        if len(clean_text) < 50:
            clean_text = self.clean_html_to_text(html)

        content_hash = hashlib.md5((title + clean_text).encode("utf-8")).hexdigest()
        
        # ID generation
        id_match = re.search(r'/articles/(\d+)', url)
        article_id = f"art-{id_match.group(1)}" if id_match else f"art-{content_hash[:8]}"

        return Article(
            id=article_id,
            url=url,
            title=title,
            category=category,
            folder=folder,
            content=clean_text,
            summary=clean_text[:280] + ("..." if len(clean_text) > 280 else ""),
            images=images,
            lastmod=lastmod,
            hash=content_hash
        )

    def scrape_batch(self, urls_to_scrape: List[Dict[str, str]], batch_size: int = settings.SCRAPE_BATCH_SIZE) -> List[Article]:
        """Scrapes a list of URLs in polite batches with checkpoint saving."""
        checkpoint = self.load_checkpoint()
        completed = checkpoint.get("completed_urls", {})
        scraped_articles: List[Article] = []

        print(f"[Scraper] Starting polite scrape for {len(urls_to_scrape)} URLs (batch size: {batch_size})...")
        
        for i, item in enumerate(urls_to_scrape):
            url = item["url"]
            lastmod = item.get("lastmod", "")
            
            # Check if already completed and hash unchanged
            if url in completed and completed[url].get("lastmod") == lastmod:
                continue

            # Polite delay
            time.sleep(settings.SCRAPE_DELAY_SECONDS)
            
            html = self.fetch_page_html(url)
            if html:
                article = self.extract_article(url, html, lastmod)
                scraped_articles.append(article)
                completed[url] = {"lastmod": lastmod, "hash": article.hash, "id": article.id}

            # Batch checkpoint write
            if (i + 1) % batch_size == 0 or (i + 1) == len(urls_to_scrape):
                checkpoint["completed_urls"] = completed
                checkpoint["last_scraped_index"] = i + 1
                checkpoint["total_urls"] = len(urls_to_scrape)
                self.save_checkpoint(checkpoint)
                print(f"[Scraper] Processed {i + 1}/{len(urls_to_scrape)} URLs. Checkpoint updated.")

        return scraped_articles
