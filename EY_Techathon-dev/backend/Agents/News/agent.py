import os
import httpx
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# Response schemas
class NewsArticle(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    published_at: str
    image_url: Optional[str] = None


class NewsResponse(BaseModel):
    status: str
    total_results: int
    articles: list[NewsArticle]


# Pharmacy & Pharmaceutical Industry Keywords (STRICT)
PHARMA_KEYWORDS = [
    "pharmaceutical",
    "pharma",
    "drug approval",
    "FDA approval",
    "EMA approval",
    "patent",
    "biotech",
    "biopharmaceutical",
    "medication",
    "drug development",
    "clinical trial",
    "vaccine",
]

# Market & Business Keywords
MARKET_KEYWORDS = [
    "market",
    "market size",
    "revenue",
    "pricing",
    "sales",
    "quarterly earnings",
    "acquisition",
    "merger",
    "IPO",
    "stock",
    "valuation",
    "investment",
    "funding",
    "partnership",
]

# Patent Keywords
PATENT_KEYWORDS = [
    "patent",
    "patent filing",
    "patent approval",
    "intellectual property",
    "trademark",
    "exclusivity",
    "generic",
    "off-patent",
    "patent expiration",
    "patent litigation",
]

# Exclude these terms to filter out unrelated news
EXCLUDE_KEYWORDS = [
    "hospital",
    "doctor",
    "patient",
    "treatment plan",
    "surgery",
    "symptoms",
    "diagnosis",
    "health tips",
    "diet",
    "fitness",
    "mental health",
    "covid",
]

NEWS_API_BASE_URL = "https://newsapi.org/v2"


def _is_relevant_pharma_news(title: str, description: str) -> bool:
    """Strict filtering for pharmacy/pharma/market/patent news."""
    content = f"{title} {description}".lower()
    
    # Must have at least one pharma keyword
    has_pharma = any(k in content for k in PHARMA_KEYWORDS)
    
    # Should have market OR patent context for business relevance
    has_business = any(k in content for k in MARKET_KEYWORDS + PATENT_KEYWORDS)
    
    # Must NOT contain excluded terms
    has_excluded = any(k in content for k in EXCLUDE_KEYWORDS)
    
    # Return true only if it's pharma + business-related and not lifestyle
    return has_pharma and has_business and not has_excluded


def _categorize_news(title: str, description: str) -> str:
    """Categorize news as Patent, Market, or Pipeline."""
    content = f"{title} {description}".lower()
    
    if any(k in content for k in PATENT_KEYWORDS):
        return "🏛️ Patent"
    elif any(k in content for k in ["clinical trial", "drug development", "approval"]):
        return "🧪 Pipeline"
    elif any(k in content for k in MARKET_KEYWORDS):
        return "📊 Market"
    return "📰 News"


async def fetch_medicine_news(
    page: int = 1, page_size: int = 20, language: str = "en"
) -> NewsResponse:
    """
    Fetch news articles related to PHARMACEUTICAL INDUSTRY: patents, markets, drug development.
    Strict filtering to exclude lifestyle/health tips content.
    """
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return NewsResponse(status="error", total_results=0, articles=[])

    # Build targeted query: pharma + (market OR patent OR approval)
    # This gets NewsAPI results that are more likely pharmaceutical industry focused
    query = "(pharmaceutical OR pharma OR biotech) AND (patent OR market OR approval OR clinical OR drug development)"

    params = {
        "q": query,
        "language": language,
        "page": page,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": api_key,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{NEWS_API_BASE_URL}/everything", params=params, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                title = article.get("title", "")
                description = article.get("description") or ""
                
                # STRICT filtering: Only include pharma+market/patent news, exclude lifestyle
                if _is_relevant_pharma_news(title, description):
                    category = _categorize_news(title, description)
                    articles.append(
                        NewsArticle(
                            title=f"{category} {title}",
                            description=description,
                            url=article.get("url", ""),
                            source=article.get("source", {}).get("name", "Unknown"),
                            published_at=article.get("publishedAt", ""),
                            image_url=article.get("urlToImage"),
                        )
                    )

            return NewsResponse(
                status="success", total_results=len(articles), articles=articles
            )

        except httpx.HTTPStatusError as e:
            return NewsResponse(
                status=f"error: {e.response.status_code}", total_results=0, articles=[]
            )
        except Exception as e:
            return NewsResponse(status=f"error: {str(e)}", total_results=0, articles=[])


class NewsAgent:
    """Class-based wrapper to fetch real-time news using NewsAPI."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

    async def fetch_medicine_news(self, page: int = 1, page_size: int = 20, language: str = "en") -> NewsResponse:
        # Reuse module-level implementation but ensure API key presence
        if not self.api_key:
            return NewsResponse(status="error", total_results=0, articles=[])
        # Temporarily set env for the inner function if needed
        os.environ.setdefault("NEWS_API_KEY", self.api_key)
        return await fetch_medicine_news(page=page, page_size=page_size, language=language)

    async def fetch_news_by_topic(self, topic: str = "medicine", page: int = 1, page_size: int = 20, language: str = "en") -> NewsResponse:
        if not self.api_key:
            return NewsResponse(status="error", total_results=0, articles=[])
        os.environ.setdefault("NEWS_API_KEY", self.api_key)
        return await fetch_news_by_topic(topic=topic, page=page, page_size=page_size)


class NewsCache:
    """Singleton cache for periodic news updates."""
    _instance = None
    _cached_news: NewsResponse | None = None
    _last_update: float = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_cached_news(self) -> NewsResponse | None:
        return self._cached_news

    def update_cache(self, news: NewsResponse):
        self._cached_news = news
        import time
        self._last_update = time.time()

    def get_last_update(self) -> float:
        return self._last_update


async def fetch_news_by_topic(
    topic: str = "pharmaceutical", page: int = 1, page_size: int = 20
) -> NewsResponse:
    """
    Fetch news for pharmaceutical/pharma/patent topics with strict industry filtering.
    """
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return NewsResponse(status="error", total_results=0, articles=[])

    # Build pharmaceutical-focused query
    enhanced_query = f'"{topic}" AND (pharmaceutical OR pharma OR biotech OR drug) AND (market OR patent OR approval OR clinical)'

    params = {
        "q": enhanced_query,
        "language": "en",
        "page": page,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "apiKey": api_key,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{NEWS_API_BASE_URL}/everything", params=params, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                title = article.get("title", "")
                description = article.get("description") or ""
                
                # Apply strict filtering
                if _is_relevant_pharma_news(title, description):
                    category = _categorize_news(title, description)
                    articles.append(
                        NewsArticle(
                            title=f"{category} {title}",
                            description=description,
                            url=article.get("url", ""),
                            source=article.get("source", {}).get("name", "Unknown"),
                            published_at=article.get("publishedAt", ""),
                            image_url=article.get("urlToImage"),
                        )
                    )

            return NewsResponse(
                status="success", total_results=len(articles), articles=articles
            )

        except Exception as e:
            return NewsResponse(status=f"error: {str(e)}", total_results=0, articles=[])