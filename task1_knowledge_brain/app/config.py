"""
Configuration settings for Task 1: The Knowledge Brain.
"""

import os

class Settings:
    SITEMAP_URL: str = os.getenv("SITEMAP_URL", "https://support.brilliantdirectories.com/support/sitemap.xml")
    DATA_DIR: str = os.getenv("KB_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
    CHECKPOINT_FILE: str = os.path.join(DATA_DIR, "scraper_checkpoint.json")
    ARTICLES_FILE: str = os.path.join(DATA_DIR, "articles_store.json")
    ESCALATIONS_FILE: str = os.path.join(DATA_DIR, "escalations_store.json")
    
    SCRAPE_BATCH_SIZE: int = int(os.getenv("SCRAPE_BATCH_SIZE", "10"))
    SCRAPE_DELAY_SECONDS: float = float(os.getenv("SCRAPE_DELAY_SECONDS", "0.5"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.62"))
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    FAST_MODEL: str = os.getenv("FAST_MODEL", "claude-3-haiku-20240307")
    
    PORT: int = int(os.getenv("PORT_TASK1", "8001"))

    # JWT Authentication Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "ai-tech-consultant-jwt-secret-key-2026-production-secure-enterprise-auth-992")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
