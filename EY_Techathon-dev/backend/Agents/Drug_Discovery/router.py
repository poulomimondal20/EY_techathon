from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid
from datetime import datetime

from .workflow import DrugDiscoveryWorkflow
from .schemas import (
    DrugDiscoveryRequest,
    WorkflowResponse,
    WorkflowStatusResponse,
    HealthCheckResponse,
    ErrorResponse,
    AgentOutput
)

router = APIRouter(
    prefix="/api/v1/drug-discovery",
    tags=["Drug Discovery Workflow"]
)

# In-memory storage for workflow results (use Redis/DB in production)
workflow_storage: Dict[str, Dict[str, Any]] = {}


@router.post("/execute", response_model=WorkflowResponse, status_code=200)
async def execute_drug_discovery_workflow(
    request: DrugDiscoveryRequest
):
    """
    Execute the drug discovery workflow synchronously.
    
    This endpoint initiates a multi-agent workflow including:
    - Target Discovery
    - Lead Identification
    - Lead Optimization
    - Preclinical Evaluation
    - Coordinator Compilation
    
    Returns complete workflow results.
    """
    workflow_id = str(uuid.uuid4())
    
    try:
        # Create and execute workflow
        workflow = DrugDiscoveryWorkflow()
        results = workflow.execute_workflow(request.query)
        
        # Prepare response
        workflow_data = {
            "workflow_id": workflow_id,
            "query": request.query,
            "execution_start": results["execution_start"],
            "execution_end": results["execution_end"],
            "workflow_status": "complete",
            "agent_outputs": {
                name: AgentOutput(**output).dict()
                for name, output in results["agent_outputs"].items()
            },
            "coordinator_response": results.get("coordinator_response", ""),
            "structured_output": results.get("structured_output")
        }
        
        # Store results
        workflow_storage[workflow_id] = workflow_data
        
        return WorkflowResponse(**workflow_data)
        
    except Exception as e:
        workflow_data = {
            "workflow_id": workflow_id,
            "query": request.query,
            "execution_start": datetime.now().isoformat(),
            "execution_end": datetime.now().isoformat(),
            "workflow_status": "failed",
            "agent_outputs": {},
            "coordinator_response": f"Workflow failed: {str(e)}"
        }
        workflow_storage[workflow_id] = workflow_data
        
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/status/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Check the status of a workflow execution.
    
    Returns current progress of all agents and overall workflow status.
    """
    if workflow_id not in workflow_storage:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    workflow_data = workflow_storage[workflow_id]
    
    progress = {}
    for agent_name, output in workflow_data.get("agent_outputs", {}).items():
        progress[agent_name] = output.get("status", "pending")
    
    status_message = {
        "complete": "Workflow completed successfully",
        "failed": "Workflow execution failed"
    }.get(workflow_data["workflow_status"], "Unknown status")
    
    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=workflow_data["workflow_status"],
        progress=progress,
        message=status_message
    )


@router.get("/results/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_results(workflow_id: str):
    """
    Retrieve complete results of a workflow execution.
    
    Returns all agent outputs and the final coordinator compilation.
    """
    if workflow_id not in workflow_storage:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    workflow_data = workflow_storage[workflow_id]
    
    return WorkflowResponse(**workflow_data)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify API and agent availability.
    """
    try:
        # Check if agents can be instantiated
        test_workflow = DrugDiscoveryWorkflow()
        agents_available = {
            "TargetDiscoveryAgent": hasattr(test_workflow, "target_discovery_agent"),
            "LeadIdentificationAgent": hasattr(test_workflow, "lead_identification_agent"),
            "LeadOptimizationAgent": hasattr(test_workflow, "lead_optimization_agent"),
            "PreclinicalEvaluationAgent": hasattr(test_workflow, "preclinical_evaluation_agent"),
            "CoordinatorAgent": hasattr(test_workflow, "coordinator_agent")
        }
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            agents_available=agents_available
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            agents_available={},
        )


@router.delete("/workflow/{workflow_id}")
async def delete_workflow_results(workflow_id: str):
    """
    Delete stored workflow results.
    """
    if workflow_id not in workflow_storage:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    del workflow_storage[workflow_id]
    
    return {"message": f"Workflow {workflow_id} deleted successfully"}


@router.get("/workflows")
async def list_workflows():
    """
    List all workflow executions with their current status.
    """
    return {
        "total_workflows": len(workflow_storage),
        "workflows": [
            {
                "workflow_id": wf_id,
                "status": wf_data["workflow_status"],
                "query": wf_data["query"][:100] + "..." if len(wf_data["query"]) > 100 else wf_data["query"],
                "execution_start": wf_data["execution_start"]
            }
            for wf_id, wf_data in workflow_storage.items()
        ]
    }













