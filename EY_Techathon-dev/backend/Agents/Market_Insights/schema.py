from pydantic import BaseModel, Field
from typing import List, Optional

class MarketAnalysisRequest(BaseModel):
    query: str = Field(..., description="Query for market analysis")

class MarketAnalysisData(BaseModel):
    market_overview: str = Field(..., description="Overview of the pharmaceutical market")
    market_size: Optional[str] = Field(None, description="Current market size and growth projections")
    key_players: List[str] = Field(default_factory=list, description="Major companies and their market positions")
    pricing_analysis: str = Field(..., description="Pricing trends and recommendations")
    competitive_landscape: List[str] = Field(default_factory=list, description="Competitive insights")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations")

class MarketAnalysisResponse(BaseModel):
    data: Optional[MarketAnalysisData] = None
    status: str = "success"
    error: Optional[str] = None
