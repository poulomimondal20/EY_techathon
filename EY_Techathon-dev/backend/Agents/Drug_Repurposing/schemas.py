from typing import List, Optional
from pydantic import BaseModel, Field


# ============== Input Schemas ==============

class DrugRepurposingRequest(BaseModel):
    """Request schema for drug repurposing analysis"""
    drug_name: str = Field(..., description="Name of the drug to analyze for repurposing")
    max_results: Optional[int] = Field(15, description="Maximum number of literature results to consider", ge=1, le=50)
    full_analysis: Optional[bool] = Field(True, description="Whether to perform full analysis with web search")


# ============== Output Schemas ==============

class SimilarDrug(BaseModel):
    """Schema for a similar drug found during analysis"""
    drug_name: str = Field(..., description="Name of the similar drug")
    current_indication: str = Field(..., description="Current approved indication/use of the drug")
    similarity_score: float = Field(..., description="Structural similarity score (0-1)", ge=0, le=1)
    mechanism_of_action: Optional[str] = Field(None, description="Mechanism of action if known")


class RepurposingCandidate(BaseModel):
    """Schema for a repurposing candidate prediction"""
    predicted_indication: str = Field(..., description="Predicted new therapeutic indication")
    confidence_score: float = Field(..., description="Confidence score for this prediction (0-1)", ge=0, le=1)
    evidence_strength: str = Field(..., description="Evidence strength: High, Medium, or Low")
    supporting_evidence: List[str] = Field(default_factory=list, description="List of supporting evidence points")
    similar_approved_drugs: List[str] = Field(default_factory=list, description="Similar drugs already approved for this indication")


class DrugProfile(BaseModel):
    """Schema for the drug being analyzed"""
    drug_name: str = Field(..., description="Name of the drug")
    smiles: Optional[str] = Field(None, description="SMILES structure of the drug")
    original_indication: Optional[str] = Field(None, description="Original approved indication")
    drug_class: Optional[str] = Field(None, description="Drug class/category")
    mechanism_of_action: Optional[str] = Field(None, description="Known mechanism of action")


class DrugRepurposingResult(BaseModel):
    """Main output schema for drug repurposing analysis"""
    summary: str = Field(..., description="Executive summary of the repurposing analysis")
    drug_profile: DrugProfile = Field(..., description="Profile of the analyzed drug")
    repurposing_candidates: List[RepurposingCandidate] = Field(
        default_factory=list, 
        description="List of potential repurposing candidates ranked by confidence"
    )
    similar_drugs: List[SimilarDrug] = Field(
        default_factory=list, 
        description="List of structurally similar drugs that informed the analysis"
    )
    clinical_considerations: List[str] = Field(
        default_factory=list, 
        description="Clinical considerations for repurposing (safety, dosing, etc.)"
    )
    research_gaps: List[str] = Field(
        default_factory=list, 
        description="Identified gaps requiring further research"
    )
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Strategic recommendations for drug repurposing"
    )
    data_sources: List[str] = Field(
        default_factory=list, 
        description="Data sources used in the analysis"
    )


class QuickPredictionResult(BaseModel):
    """Schema for quick prediction result using PubMed and PubChem"""
    drug_name: str = Field(..., description="Name of the drug analyzed")
    drug_info: dict = Field(default_factory=dict, description="Drug information from PubChem")
    literature: dict = Field(default_factory=dict, description="Relevant literature from PubMed")
    clinical_trials: dict = Field(default_factory=dict, description="Ongoing clinical trials")


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error message describing what went wrong")
    drug_name: Optional[str] = Field(None, description="Drug name that caused the error")