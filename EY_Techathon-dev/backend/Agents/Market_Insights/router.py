from fastapi import APIRouter, HTTPException
from .schema import MarketAnalysisRequest, MarketAnalysisResponse, MarketAnalysisData
from .agent import MarketInsightsAgent

router = APIRouter(
    prefix="/api/v1/market-insights",
    tags=["Market Insights"]
)

market_agent = MarketInsightsAgent()

@router.post("/analyze", response_model=MarketAnalysisResponse)
async def analyze_market(request: MarketAnalysisRequest):
    """
    Analyze pharmaceutical market for given query.
    
    Returns:
    - Structured JSON analysis with market overview, pricing, and recommendations
    """
    try:
        result = market_agent.analyze_market(request.query)
        return MarketAnalysisResponse(
            data=MarketAnalysisData(
                market_overview=result.market_overview,
                market_size=result.market_size,
                key_players=result.key_players,
                pricing_analysis=result.pricing_analysis,
                competitive_landscape=result.competitive_landscape,
                strategic_recommendations=result.strategic_recommendations
            ),
            status="success"
        )
    except Exception as e:
        return MarketAnalysisResponse(
            data=None,
            status="error",
            error=str(e)
        )
