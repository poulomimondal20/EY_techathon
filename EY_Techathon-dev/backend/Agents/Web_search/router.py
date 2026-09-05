from fastapi import APIRouter, HTTPException, status
from .web_search_agent import WebSearchAgent
from .schemas import WebSearchRequest, WebSearchResponse
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/web-search",
    tags=["Web Search"]
)

_agent_instance = None


def get_agent() -> WebSearchAgent:
    """Get or create web search agent instance"""
    global _agent_instance
    if _agent_instance is None:
        logger.info("Initializing Web Search Agent...")
        _agent_instance = WebSearchAgent()
    return _agent_instance


@router.post(
    "/search",
    response_model=WebSearchResponse,
    summary="Perform web search and research",
    description="Comprehensive web search across multiple sources with fact-checking and source verification"
)
async def web_search(request: WebSearchRequest) -> WebSearchResponse:
    """
    Perform comprehensive web search and research.
    
    - **query**: Search query or research question
    
    Returns detailed search results with sources.
    """
    try:
        logger.info(f"Processing web search: {request.query[:100]}...")
        
        agent = get_agent()
        search_results = agent.research_question(request.query)
        
        response = WebSearchResponse(
            query=request.query,
            status="success",
            search_results=search_results,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("Successfully completed web search")
        return response
        
    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )
