from fastapi import APIRouter, Query
from .agent import NewsAgent, NewsCache
from .schemas import NewsResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/news",
    tags=["News"],
)

_agent = NewsAgent()
_cache = NewsCache()


@router.get("/cached", response_model=NewsResponse, summary="Get cached news (auto-updated every 10 min)")
async def get_cached_news():
    """Returns cached news that's automatically refreshed in background."""
    cached = _cache.get_cached_news()
    if cached:
        return cached
    # Fallback: fetch live if cache is empty
    logger.info("Cache empty, fetching live news")
    return await _agent.fetch_medicine_news(page=1, page_size=15, language="en")


@router.get("/medicine", response_model=NewsResponse, summary="Latest medicine/drug related news")
async def get_medicine_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    language: str = Query("en")
):
    return await _agent.fetch_medicine_news(page=page, page_size=page_size, language=language)


@router.get("/topic/{topic}", response_model=NewsResponse, summary="News by topic with medical focus")
async def get_news_by_topic(
    topic: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    language: str = Query("en")
):
    return await _agent.fetch_news_by_topic(topic=topic, page=page, page_size=page_size, language=language)


async def fetch_and_cache_news():
    """Background task to periodically fetch and cache news."""
    try:
        logger.info("Fetching latest medicine news for cache...")
        news = await _agent.fetch_medicine_news(page=1, page_size=15, language="en")
        _cache.update_cache(news)
        logger.info(f"Cached {news.total_results} news articles")
    except Exception as e:
        logger.error(f"Failed to fetch news for cache: {e}")
