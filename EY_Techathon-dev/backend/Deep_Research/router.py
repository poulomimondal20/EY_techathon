"""
FastAPI Router for Deep Medical Research Pipeline.

Provides RESTful API endpoints for:
- Comprehensive medical research queries
- Quick literature searches
- Drug information lookups
- Clinical trial searches
- Research status tracking
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import asyncio

from .orchestrator import MedicalResearchPipeline
from .schemas import (
    DeepResearchRequest,
    DeepResearchResponse,
    QuickSearchRequest,
    QuickSearchResponse,
    DrugLookupRequest,
    ClinicalTrialSearchRequest,
    ResearchStatusResponse,
    HealthCheckResponse,
    ErrorResponse
)


router = APIRouter(
    prefix="/api/v1/deep-research",
    tags=["Deep Medical Research"]
)

# In-memory storage for research results (use Redis/DB in production)
research_storage: Dict[str, Dict[str, Any]] = {}

# Pipeline instance (lazy initialization)
_pipeline: Optional[MedicalResearchPipeline] = None


def get_pipeline() -> MedicalResearchPipeline:
    """Get or create the research pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = MedicalResearchPipeline()
    return _pipeline


async def execute_research_task(
    research_id: str,
    request: DeepResearchRequest
):
    """Background task to execute research."""
    try:
        pipeline = get_pipeline()
        
        # Update status to running
        research_storage[research_id]["status"] = "running"
        
        # Execute research
        results = await pipeline.research(
            query=request.query,
            mode=request.mode,
            include_clinical_trials=request.include_clinical_trials,
            include_drug_info=request.include_drug_info,
            output_format=request.output_format
        )
        
        # Update storage with results
        research_storage[research_id].update({
            "status": "complete",
            "papers": results.get("literature_results", results.get("papers", [])),
            "trials": results.get("clinical_trial_results", results.get("trials", [])),
            "drugs": results.get("drug_results", results.get("drugs", [])),
            "synthesis": results.get("synthesis", ""),
            "gaps": results.get("gaps_identified", results.get("gaps", [])),
            "recommendations": results.get("recommendations", []),
            "critique": results.get("critique_results", results.get("critique", {})),
            "execution_time": results.get("execution_time", 0),
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        research_storage[research_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


@router.post("/execute", response_model=DeepResearchResponse, status_code=200)
async def execute_deep_research(request: DeepResearchRequest):
    """
    Execute a comprehensive deep medical research query synchronously.
    
    This endpoint initiates a multi-agent research pipeline including:
    - Literature search (PubMed)
    - Clinical trials analysis
    - Drug/therapeutic information
    - AI-powered synthesis
    - Quality critique
    
    Returns complete research results.
    """
    research_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        pipeline = get_pipeline()
        
        # Execute research
        results = await pipeline.research(
            query=request.query,
            mode=request.mode,
            include_clinical_trials=request.include_clinical_trials,
            include_drug_info=request.include_drug_info,
            output_format=request.output_format
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response
        response_data = {
            "research_id": research_id,
            "query": request.query,
            "status": "complete",
            "execution_time": execution_time,
            "papers": results.get("literature_results", results.get("papers", [])),
            "trials": results.get("clinical_trial_results", results.get("trials", [])),
            "drugs": results.get("drug_results", results.get("drugs", [])),
            "synthesis": results.get("synthesis", ""),
            "gaps": results.get("gaps_identified", results.get("gaps", [])),
            "recommendations": results.get("recommendations", []),
            "critique": results.get("critique_results", results.get("critique", {})),
            "structured_output": results.get("structured_output"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store results
        research_storage[research_id] = response_data
        
        return DeepResearchResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Research execution failed: {str(e)}"
        )


@router.post("/execute/async", status_code=202)
async def execute_deep_research_async(
    request: DeepResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a deep research query asynchronously.
    
    Returns immediately with a research_id that can be used to 
    check status and retrieve results via /status/{research_id}.
    """
    research_id = str(uuid.uuid4())
    
    # Initialize storage entry
    research_storage[research_id] = {
        "research_id": research_id,
        "query": request.query,
        "status": "pending",
        "papers": [],
        "trials": [],
        "drugs": [],
        "synthesis": None,
        "gaps": [],
        "recommendations": [],
        "critique": None,
        "execution_time": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add background task
    background_tasks.add_task(execute_research_task, research_id, request)
    
    return {
        "research_id": research_id,
        "status": "pending",
        "message": "Research started. Use /status/{research_id} to check progress.",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/status/{research_id}", response_model=ResearchStatusResponse)
async def get_research_status(research_id: str):
    """
    Check the status of a research execution.
    
    Returns current progress and status of the research query.
    """
    if research_id not in research_storage:
        return ResearchStatusResponse(
            research_id=research_id,
            status="not_found",
            progress={},
            message=f"Research {research_id} not found",
            timestamp=datetime.now().isoformat()
        )
    
    research_data = research_storage[research_id]
    status = research_data.get("status", "unknown")
    
    progress = {
        "literature": "complete" if research_data.get("papers") else "pending",
        "clinical_trials": "complete" if research_data.get("trials") else "pending",
        "drugs": "complete" if research_data.get("drugs") else "pending",
        "synthesis": "complete" if research_data.get("synthesis") else "pending",
        "critique": "complete" if research_data.get("critique") else "pending"
    }
    
    messages = {
        "pending": "Research is queued for execution",
        "running": "Research is in progress",
        "complete": "Research completed successfully",
        "failed": f"Research failed: {research_data.get('error', 'Unknown error')}"
    }
    
    return ResearchStatusResponse(
        research_id=research_id,
        status=status,
        progress=progress,
        message=messages.get(status, "Unknown status"),
        timestamp=datetime.now().isoformat()
    )


@router.get("/results/{research_id}", response_model=DeepResearchResponse)
async def get_research_results(research_id: str):
    """
    Retrieve the results of a completed research query.
    """
    if research_id not in research_storage:
        raise HTTPException(
            status_code=404, 
            detail=f"Research {research_id} not found"
        )
    
    research_data = research_storage[research_id]
    
    if research_data.get("status") == "pending":
        raise HTTPException(
            status_code=202, 
            detail="Research is still pending"
        )
    
    if research_data.get("status") == "running":
        raise HTTPException(
            status_code=202, 
            detail="Research is still in progress"
        )
    
    if research_data.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {research_data.get('error', 'Unknown error')}"
        )
    
    return DeepResearchResponse(**research_data)


@router.post("/quick-search", response_model=QuickSearchResponse)
async def quick_literature_search(request: QuickSearchRequest):
    """
    Perform a quick literature search without full analysis.
    
    Returns papers from PubMed matching the query.
    """
    try:
        pipeline = get_pipeline()
        results = await pipeline.quick_search(request.query)
        
        return QuickSearchResponse(
            query=request.query,
            papers=results.get("papers", []),
            count=results.get("count", 0),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick search failed: {str(e)}"
        )


@router.post("/drug-lookup")
async def lookup_drug_info(request: DrugLookupRequest):
    """
    Look up information about a specific drug.
    
    Returns drug details, mechanism, indications, and optionally interactions.
    """
    try:
        pipeline = get_pipeline()
        results = await pipeline.analyze_drug(request.drug_name)
        
        return {
            "drug_name": request.drug_name,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Drug lookup failed: {str(e)}"
        )


@router.post("/clinical-trials")
async def search_clinical_trials(request: ClinicalTrialSearchRequest):
    """
    Search for clinical trials by condition, intervention, or status.
    """
    try:
        pipeline = get_pipeline()
        results = await pipeline.find_clinical_trials(
            condition=request.condition,
            intervention=request.intervention,
            status=request.status
        )
        
        return {
            "search_criteria": {
                "condition": request.condition,
                "intervention": request.intervention,
                "status": request.status
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Clinical trial search failed: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check the health status of the Deep Research Pipeline.
    """
    try:
        pipeline = get_pipeline()
        
        # Check component availability
        components = {
            "llm_client": pipeline.llm_client is not None,
            "tool_registry": pipeline.tool_registry is not None,
            "agent_team": pipeline.agent_team is not None,
            "workflow": pipeline.workflow is not None
        }
        
        # Check individual tools
        if pipeline.tool_registry:
            for tool_name in ["pubmed_search", "clinical_trials", "drug_info"]:
                components[f"tool_{tool_name}"] = pipeline.tool_registry.get(tool_name) is not None
        
        all_healthy = all(components.values())
        
        return HealthCheckResponse(
            status="healthy" if all_healthy else "degraded",
            service="Deep Research Pipeline API",
            timestamp=datetime.now().isoformat(),
            components=components
        )
        
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service="Deep Research Pipeline API",
            timestamp=datetime.now().isoformat(),
            components={"error": str(e)}
        )


@router.delete("/results/{research_id}")
async def delete_research_results(research_id: str):
    """
    Delete stored research results.
    """
    if research_id not in research_storage:
        raise HTTPException(
            status_code=404,
            detail=f"Research {research_id} not found"
        )
    
    del research_storage[research_id]
    
    return {
        "message": f"Research {research_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/history")
async def get_research_history():
    """
    Get a list of all stored research queries.
    """
    history = []
    for research_id, data in research_storage.items():
        history.append({
            "research_id": research_id,
            "query": data.get("query", ""),
            "status": data.get("status", "unknown"),
            "timestamp": data.get("timestamp", ""),
            "execution_time": data.get("execution_time")
        })
    
    return {
        "count": len(history),
        "history": history,
        "timestamp": datetime.now().isoformat()
    }
