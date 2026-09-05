from fastapi import APIRouter, HTTPException
from .schemas import CompetitorAnalysisRequest, CompetitorAnalysisResponse, CompetitorAnalysisData, CompetitorProfile
from .agent import CompetitorAnalysisAgent

router = APIRouter(prefix="/api/v1/competitor-analysis", tags=["Competitor Analysis"])

agent = CompetitorAnalysisAgent()

@router.post("/analyze", response_model=CompetitorAnalysisResponse)
async def analyze_competitor(request: CompetitorAnalysisRequest):
    """
    Analyze competitors based on query.
    
    Returns detailed competitive intelligence with numerical metrics.
    """
    try:
        result = agent.answer(request.query)
        
        # Convert competitor profiles
        competitor_profiles = []
        for comp in result.competitors:
            if isinstance(comp, dict):
                competitor_profiles.append(CompetitorProfile(**comp))
            else:
                competitor_profiles.append(CompetitorProfile(
                    name=comp.name,
                    market_share=comp.market_share,
                    revenue=comp.revenue,
                    active_trials=comp.active_trials,
                    pipeline_drugs=comp.pipeline_drugs,
                    key_products=comp.key_products,
                    strengths=comp.strengths,
                    weaknesses=comp.weaknesses
                ))
        
        return CompetitorAnalysisResponse(
            data=CompetitorAnalysisData(
                overview=result.overview,
                market_size=result.market_size,
                market_growth_rate=result.market_growth_rate,
                total_competitors=result.total_competitors,
                competitors=competitor_profiles,
                pipeline_insights=result.pipeline_insights,
                market_trends=result.market_trends,
                threats=result.threats,
                opportunities=result.opportunities,
                recommendations=result.recommendations
            ),
            status="success"
        )
    except Exception as e:
        return CompetitorAnalysisResponse(
            data=None,
            status="error",
            error=str(e)
        )
