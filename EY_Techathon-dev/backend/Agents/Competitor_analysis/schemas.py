from pydantic import BaseModel, Field
from typing import List, Optional

class CompetitorAnalysisRequest(BaseModel):
    query: str = Field(..., description="Natural language query for competitor analysis")

class CompetitorProfile(BaseModel):
    name: str = Field(..., description="Competitor company name")
    market_share: Optional[str] = Field(None, description="Estimated market share percentage")
    revenue: Optional[str] = Field(None, description="Annual revenue in this segment")
    active_trials: Optional[int] = Field(None, description="Number of active clinical trials")
    pipeline_drugs: Optional[int] = Field(None, description="Number of drugs in pipeline")
    key_products: List[str] = Field(default_factory=list, description="Key products with sales")
    strengths: List[str] = Field(default_factory=list, description="Competitive strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Competitive weaknesses")

class CompetitorAnalysisData(BaseModel):
    overview: str = Field(..., description="Executive summary with key numbers")
    market_size: Optional[str] = Field(None, description="Total addressable market size")
    market_growth_rate: Optional[str] = Field(None, description="Annual growth rate (CAGR)")
    total_competitors: Optional[int] = Field(None, description="Number of major competitors")
    competitors: List[CompetitorProfile] = Field(default_factory=list, description="Competitor profiles")
    pipeline_insights: List[str] = Field(default_factory=list, description="Pipeline insights with numbers")
    market_trends: List[str] = Field(default_factory=list, description="Market trends with data")
    threats: List[str] = Field(default_factory=list, description="Competitive threats")
    opportunities: List[str] = Field(default_factory=list, description="Market opportunities with value")
    recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations")

class CompetitorAnalysisResponse(BaseModel):
    data: Optional[CompetitorAnalysisData] = None
    status: str = "success"
    error: Optional[str] = None
