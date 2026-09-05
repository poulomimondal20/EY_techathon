from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal, List
from datetime import datetime


class DrugDiscoveryRequest(BaseModel):
    """Request schema for drug discovery workflow"""
    query: str = Field(
        ..., 
        description="The therapeutic query or drug discovery problem",
        min_length=10,
        example="Develop a novel therapeutic for Alzheimer's disease targeting tau protein aggregation"
    )
    

class AgentOutput(BaseModel):
    """Schema for individual agent output"""
    status: Literal["success", "error", "pending"] = Field(..., description="Execution status")
    content: Optional[str] = Field(None, description="Agent response content")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: str = Field(..., description="ISO formatted timestamp")


# ============================================================================
# Structured Output Models for Drug Discovery
# ============================================================================

class TargetInfo(BaseModel):
    """Structured target information"""
    target_name: str = Field(..., description="Name of the therapeutic target")
    target_type: Optional[str] = Field(None, description="Type of target (protein, gene, pathway)")
    gene_symbol: Optional[str] = Field(None, description="Gene symbol if applicable")
    uniprot_id: Optional[str] = Field(None, description="UniProt identifier")
    validation_score: Optional[float] = Field(None, description="Target validation score (0-10)")
    disease_association: Optional[str] = Field(None, description="Associated disease/condition")
    druggability_assessment: Optional[str] = Field(None, description="Druggability assessment")
    known_modulators: List[str] = Field(default_factory=list, description="Known modulators/drugs")


class LeadCompound(BaseModel):
    """Structured lead compound information"""
    compound_id: str = Field(..., description="Compound identifier")
    smiles: Optional[str] = Field(None, description="SMILES notation")
    molecular_weight: Optional[float] = Field(None, description="Molecular weight (Da)")
    logp: Optional[float] = Field(None, description="LogP value")
    binding_affinity: Optional[str] = Field(None, description="Binding affinity (IC50/Ki)")
    selectivity: Optional[str] = Field(None, description="Selectivity profile")
    lead_score: Optional[float] = Field(None, description="Overall lead score (0-10)")
    lipinski_violations: Optional[int] = Field(None, description="Lipinski rule violations")
    source: Optional[str] = Field(None, description="Source of compound")


class OptimizationResult(BaseModel):
    """Structured optimization results"""
    optimized_compound_id: str = Field(..., description="Optimized compound ID")
    parent_compound_id: Optional[str] = Field(None, description="Parent compound ID")
    modifications: List[str] = Field(default_factory=list, description="Structural modifications made")
    improved_properties: Dict[str, str] = Field(default_factory=dict, description="Improved properties")
    admet_profile: Dict[str, Any] = Field(default_factory=dict, description="ADMET properties")
    optimization_score: Optional[float] = Field(None, description="Optimization score (0-10)")
    synthetic_accessibility: Optional[float] = Field(None, description="Synthetic accessibility score")


class PreclinicalData(BaseModel):
    """Structured preclinical evaluation data"""
    candidate_id: str = Field(..., description="Candidate compound ID")
    toxicity_assessment: Dict[str, Any] = Field(default_factory=dict, description="Toxicity assessment")
    efficacy_data: Dict[str, Any] = Field(default_factory=dict, description="Efficacy data")
    pharmacokinetics: Dict[str, Any] = Field(default_factory=dict, description="PK parameters")
    safety_score: Optional[float] = Field(None, description="Overall safety score (0-10)")
    efficacy_score: Optional[float] = Field(None, description="Overall efficacy score (0-10)")
    recommendation: Optional[str] = Field(None, description="GO/NO-GO recommendation")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")


class RiskAssessment(BaseModel):
    """Risk assessment entry"""
    risk_category: str = Field(..., description="Category of risk")
    source_agent: str = Field(..., description="Agent that identified this risk")
    severity: Literal["High", "Medium", "Low"] = Field(..., description="Risk severity")
    impact: str = Field(..., description="Potential impact description")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy")


class StrategicDecision(BaseModel):
    """Strategic decision framework"""
    recommendation: Literal["GO", "CONDITIONAL_GO", "NO_GO"] = Field(..., description="Final recommendation")
    scientific_merit_score: float = Field(..., description="Scientific merit score (0-10)")
    technical_feasibility_score: float = Field(..., description="Technical feasibility score (0-10)")
    safety_profile_score: float = Field(..., description="Safety profile score (0-10)")
    commercial_viability_score: float = Field(..., description="Commercial viability score (0-10)")
    overall_score: float = Field(..., description="Weighted overall score (0-10)")
    critical_success_factors: List[str] = Field(default_factory=list, description="Critical success factors")
    red_flags: List[str] = Field(default_factory=list, description="Red flags or deal breakers")


class ActionItem(BaseModel):
    """Actionable roadmap item"""
    action: str = Field(..., description="Action description")
    timeframe: Literal["immediate", "near_term", "long_term"] = Field(..., description="Timeframe")
    priority: Literal["High", "Medium", "Low"] = Field(..., description="Priority level")
    responsible_party: Optional[str] = Field(None, description="Responsible party/team")
    resources_required: Optional[str] = Field(None, description="Resources required")


class DrugDiscoveryStructuredOutput(BaseModel):
    """Comprehensive structured output for drug discovery workflow"""
    
    # Metadata
    workflow_id: str = Field(..., description="Unique workflow execution ID")
    query: str = Field(..., description="Original therapeutic query")
    execution_start: str = Field(..., description="Workflow start timestamp")
    execution_end: Optional[str] = Field(None, description="Workflow end timestamp")
    workflow_status: Literal["running", "complete", "failed"] = Field(..., description="Workflow status")
    
    # Target Discovery Results
    target_discovery: Optional[TargetInfo] = Field(None, description="Target discovery results")
    target_discovery_raw: Optional[str] = Field(None, description="Raw target discovery output")
    
    # Lead Identification Results
    lead_compounds: List[LeadCompound] = Field(default_factory=list, description="Identified lead compounds")
    lead_identification_raw: Optional[str] = Field(None, description="Raw lead identification output")
    
    # Lead Optimization Results
    optimization_results: List[OptimizationResult] = Field(default_factory=list, description="Optimization results")
    optimization_raw: Optional[str] = Field(None, description="Raw optimization output")
    
    # Preclinical Evaluation Results
    preclinical_data: Optional[PreclinicalData] = Field(None, description="Preclinical evaluation data")
    preclinical_raw: Optional[str] = Field(None, description="Raw preclinical output")
    
    # Integrated Analysis
    risk_matrix: List[RiskAssessment] = Field(default_factory=list, description="Consolidated risk matrix")
    strategic_decision: Optional[StrategicDecision] = Field(None, description="Strategic decision framework")
    action_roadmap: List[ActionItem] = Field(default_factory=list, description="Actionable roadmap")
    
    # Executive Summary
    executive_summary: Optional[str] = Field(None, description="Executive summary of findings")
    cross_agent_insights: List[str] = Field(default_factory=list, description="Cross-agent insights")
    
    # Coordinator Response
    coordinator_response: Optional[str] = Field(None, description="Full coordinator compilation")


class WorkflowResponse(BaseModel):
    """Response schema for workflow execution"""
    workflow_id: str = Field(..., description="Unique workflow execution ID")
    query: str = Field(..., description="Original query")
    execution_start: str = Field(..., description="Workflow start time")
    execution_end: Optional[str] = Field(None, description="Workflow end time")
    workflow_status: Literal["running", "complete", "failed"] = Field(..., description="Overall workflow status")
    agent_outputs: Dict[str, AgentOutput] = Field(default_factory=dict, description="Individual agent results")
    coordinator_response: Optional[str] = Field(None, description="Final compiled response from coordinator")
    structured_output: Optional[DrugDiscoveryStructuredOutput] = Field(None, description="Structured output data")
    

class WorkflowStatusResponse(BaseModel):
    """Response schema for workflow status check"""
    workflow_id: str
    status: Literal["running", "complete", "failed", "not_found"]
    progress: Dict[str, str] = Field(default_factory=dict, description="Status of each agent")
    message: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    service: str = Field(default="Drug Discovery Workflow API")
    timestamp: str
    agents_available: Dict[str, bool]


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: str
