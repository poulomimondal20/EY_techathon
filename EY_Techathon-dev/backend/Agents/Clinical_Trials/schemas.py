from pydantic import BaseModel, Field
from typing import List, Optional

class ClinicalTrialRequest(BaseModel):
    query: str = Field(..., description="Query for analyzing clinical trial pipeline")

class ClinicalTrialData(BaseModel):
    pipeline_summary: str = Field(..., description="Overview of the clinical trial pipeline")
    key_trials: List[str] = Field(default_factory=list, description="List of key trials with phase and status")
    recent_updates: List[str] = Field(default_factory=list, description="Recent updates or milestones")
    strategic_insights: str = Field(..., description="Strategic analysis and recommendations")

class ClinicalTrialResponse(BaseModel):
    data: Optional[ClinicalTrialData] = None
    status: str = "success"
    error: Optional[str] = None