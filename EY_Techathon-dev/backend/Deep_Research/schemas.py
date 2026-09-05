from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime


class DeepResearchRequest(BaseModel):
    """Request schema for deep research workflow"""
    query: str = Field(
        ..., 
        description="The medical research query or question",
        min_length=5,
        example="What are the latest treatments for Type 2 Diabetes?"
    )
    mode: Literal["quick", "standard", "comprehensive"] = Field(
        default="comprehensive",
        description="Research depth mode"
    )
    include_clinical_trials: bool = Field(
        default=True,
        description="Whether to include clinical trial data"
    )
    include_drug_info: bool = Field(
        default=True,
        description="Whether to include drug/therapeutic information"
    )
    output_format: Literal["summary", "detailed", "full"] = Field(
        default="detailed",
        description="Output detail level"
    )


# ============================================================================
# Structured Output Models for Deep Research
# ============================================================================

class PaperResult(BaseModel):
    """Schema for a literature paper result"""
    title: str = Field(..., description="Paper title")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    doi: Optional[str] = Field(None, description="DOI identifier")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[str] = Field(None, description="Publication date")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    url: Optional[str] = Field(None, description="URL to the paper")
    citation_count: Optional[int] = Field(None, description="Citation count")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    study_type: Optional[str] = Field(None, description="Type of study (RCT, meta-analysis, etc.)")
    evidence_level: Optional[str] = Field(None, description="Level of evidence")


class ClinicalTrialResult(BaseModel):
    """Schema for a clinical trial result"""
    nct_id: str = Field(..., description="ClinicalTrials.gov identifier")
    title: str = Field(..., description="Trial title")
    status: str = Field(..., description="Current trial status")
    phase: Optional[str] = Field(None, description="Trial phase")
    conditions: List[str] = Field(default_factory=list, description="Conditions studied")
    interventions: List[str] = Field(default_factory=list, description="Interventions used")
    sponsor: Optional[str] = Field(None, description="Trial sponsor")
    start_date: Optional[str] = Field(None, description="Trial start date")
    completion_date: Optional[str] = Field(None, description="Expected completion date")
    enrollment: Optional[int] = Field(None, description="Target enrollment")
    primary_outcomes: List[str] = Field(default_factory=list, description="Primary outcome measures")
    url: Optional[str] = Field(None, description="URL to the trial")
    locations: List[str] = Field(default_factory=list, description="Trial locations")


class DrugResult(BaseModel):
    """Schema for a drug/therapeutic result"""
    name: str = Field(..., description="Drug name")
    generic_name: Optional[str] = Field(None, description="Generic name")
    brand_names: List[str] = Field(default_factory=list, description="Brand names")
    drug_class: Optional[str] = Field(None, description="Drug class/category")
    mechanism: Optional[str] = Field(None, description="Mechanism of action")
    fda_status: Optional[str] = Field(None, description="FDA approval status")
    approval_date: Optional[str] = Field(None, description="FDA approval date")
    indications: List[str] = Field(default_factory=list, description="Approved indications")
    contraindications: List[str] = Field(default_factory=list, description="Contraindications")
    side_effects: List[str] = Field(default_factory=list, description="Common side effects")
    interactions: List[str] = Field(default_factory=list, description="Drug interactions")
    dosage_forms: List[str] = Field(default_factory=list, description="Available dosage forms")


class EvidenceSummary(BaseModel):
    """Summary of evidence quality"""
    total_papers: int = Field(0, description="Total number of papers found")
    total_trials: int = Field(0, description="Total number of trials found")
    total_drugs: int = Field(0, description="Total number of drugs found")
    meta_analyses_count: int = Field(0, description="Number of meta-analyses")
    rct_count: int = Field(0, description="Number of RCTs")
    overall_evidence_quality: Literal["High", "Moderate", "Low", "Very Low", "Unknown"] = Field(
        "Unknown", description="Overall evidence quality assessment"
    )
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1)")


class ResearchGap(BaseModel):
    """Identified research gap"""
    gap_description: str = Field(..., description="Description of the research gap")
    gap_type: Literal["knowledge", "methodological", "population", "intervention", "outcome"] = Field(
        ..., description="Type of research gap"
    )
    priority: Literal["High", "Medium", "Low"] = Field(..., description="Priority for addressing")
    suggested_research: Optional[str] = Field(None, description="Suggested research to fill gap")


class Recommendation(BaseModel):
    """Research or clinical recommendation"""
    recommendation: str = Field(..., description="Recommendation text")
    target_audience: Literal["clinicians", "researchers", "policymakers", "patients", "general"] = Field(
        ..., description="Target audience"
    )
    strength: Literal["Strong", "Moderate", "Weak", "Conditional"] = Field(
        ..., description="Strength of recommendation"
    )
    evidence_basis: Optional[str] = Field(None, description="Evidence supporting this recommendation")


class CritiqueResult(BaseModel):
    """Schema for quality assessment/critique"""
    quality_score: float = Field(..., description="Quality score (0-10)")
    completeness_score: Optional[float] = Field(None, description="Completeness score (0-10)")
    accuracy_score: Optional[float] = Field(None, description="Accuracy score (0-10)")
    structure_score: Optional[float] = Field(None, description="Structure score (0-10)")
    clinical_relevance_score: Optional[float] = Field(None, description="Clinical relevance score (0-10)")
    overall_assessment: str = Field(..., description="Overall assessment summary")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class KeyFinding(BaseModel):
    """Key finding from the research"""
    finding: str = Field(..., description="Description of the finding")
    source_type: Literal["literature", "clinical_trial", "drug_data", "synthesis"] = Field(
        ..., description="Source type"
    )
    confidence: Literal["High", "Moderate", "Low"] = Field(..., description="Confidence level")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting evidence references")


class TherapeuticLandscape(BaseModel):
    """Overview of therapeutic landscape"""
    current_standard_of_care: Optional[str] = Field(None, description="Current standard of care")
    emerging_therapies: List[str] = Field(default_factory=list, description="Emerging therapies")
    pipeline_drugs: List[str] = Field(default_factory=list, description="Drugs in development pipeline")
    unmet_needs: List[str] = Field(default_factory=list, description="Unmet medical needs")
    market_trends: Optional[str] = Field(None, description="Market trends summary")


class DeepResearchStructuredOutput(BaseModel):
    """Comprehensive structured output for deep research workflow"""
    
    # Metadata
    research_id: str = Field(..., description="Unique research execution ID")
    query: str = Field(..., description="Original research query")
    mode: str = Field(..., description="Research mode used")
    status: Literal["running", "complete", "failed"] = Field(..., description="Research status")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: str = Field(..., description="Research completion timestamp")
    
    # Literature Results
    papers: List[PaperResult] = Field(default_factory=list, description="Literature results")
    papers_summary: Optional[str] = Field(None, description="Summary of literature findings")
    
    # Clinical Trials Results
    trials: List[ClinicalTrialResult] = Field(default_factory=list, description="Clinical trial results")
    trials_summary: Optional[str] = Field(None, description="Summary of clinical trial landscape")
    active_trials_count: int = Field(0, description="Number of active/recruiting trials")
    
    # Drug/Therapeutic Results
    drugs: List[DrugResult] = Field(default_factory=list, description="Drug/therapeutic results")
    drugs_summary: Optional[str] = Field(None, description="Summary of drug findings")
    
    # Evidence Assessment
    evidence_summary: Optional[EvidenceSummary] = Field(None, description="Evidence quality summary")
    
    # Key Findings
    key_findings: List[KeyFinding] = Field(default_factory=list, description="Key findings from research")
    
    # Therapeutic Landscape
    therapeutic_landscape: Optional[TherapeuticLandscape] = Field(None, description="Therapeutic landscape overview")
    
    # Synthesis
    executive_summary: Optional[str] = Field(None, description="Executive summary")
    synthesis: Optional[str] = Field(None, description="Full AI-generated synthesis")
    
    # Gaps and Recommendations
    research_gaps: List[ResearchGap] = Field(default_factory=list, description="Identified research gaps")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Recommendations")
    
    # Quality Assessment
    critique: Optional[CritiqueResult] = Field(None, description="Quality assessment results")
    
    # Clinical Implications
    clinical_implications: List[str] = Field(default_factory=list, description="Clinical implications")
    
    # Future Directions
    future_directions: List[str] = Field(default_factory=list, description="Future research directions")


class DeepResearchResponse(BaseModel):
    """Response schema for deep research workflow"""
    research_id: str = Field(..., description="Unique research execution ID")
    query: str = Field(..., description="Original research query")
    status: Literal["running", "complete", "failed"] = Field(..., description="Research status")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    
    # Research results (raw)
    papers: List[Dict[str, Any]] = Field(default_factory=list, description="Literature results")
    trials: List[Dict[str, Any]] = Field(default_factory=list, description="Clinical trial results")
    drugs: List[Dict[str, Any]] = Field(default_factory=list, description="Drug/therapeutic results")
    
    # Analysis
    synthesis: Optional[str] = Field(None, description="AI-generated synthesis of findings")
    gaps: List[str] = Field(default_factory=list, description="Identified research gaps")
    recommendations: List[str] = Field(default_factory=list, description="Research recommendations")
    
    # Quality assessment
    critique: Optional[Dict[str, Any]] = Field(None, description="Quality assessment results")
    
    # Structured output
    structured_output: Optional[DeepResearchStructuredOutput] = Field(None, description="Structured output data")
    
    # Metadata
    timestamp: str = Field(..., description="Research completion timestamp")


class QuickSearchRequest(BaseModel):
    """Request schema for quick literature search"""
    query: str = Field(
        ..., 
        description="Search query",
        min_length=3
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of results",
        ge=1,
        le=50
    )


class QuickSearchResponse(BaseModel):
    """Response schema for quick search"""
    query: str
    papers: List[Dict[str, Any]]
    count: int
    timestamp: str


class DrugLookupRequest(BaseModel):
    """Request schema for drug lookup"""
    drug_name: str = Field(
        ..., 
        description="Name of the drug to look up"
    )
    include_interactions: bool = Field(
        default=True,
        description="Whether to include drug interactions"
    )


class ClinicalTrialSearchRequest(BaseModel):
    """Request schema for clinical trial search"""
    condition: Optional[str] = Field(None, description="Medical condition")
    intervention: Optional[str] = Field(None, description="Treatment/intervention")
    status: Optional[List[str]] = Field(None, description="Trial status filter")


class ResearchStatusResponse(BaseModel):
    """Response schema for research status check"""
    research_id: str
    status: Literal["running", "complete", "failed", "not_found"]
    progress: Dict[str, str] = Field(default_factory=dict, description="Progress of each phase")
    message: str
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    service: str = Field(default="Deep Research Pipeline API")
    timestamp: str
    components: Dict[str, bool] = Field(default_factory=dict, description="Component availability")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: str
