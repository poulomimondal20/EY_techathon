from fastapi import APIRouter, HTTPException, Depends
from .schemas import (
    DrugRepurposingRequest,
    DrugRepurposingResult,
    ErrorResponse
)
from .agent import DrugRepurposingAgent


router = APIRouter(
    prefix="/api/v1/drug-repurposing",
    tags=["Drug Repurposing"]
)

# Singleton agent instance
_agent_instance = None

def get_agent():
    """Get or create singleton agent instance"""
    global _agent_instance
    if _agent_instance is None:
        try:
            _agent_instance = DrugRepurposingAgent()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Drug Repurposing agent: {str(e)}"
            )
    return _agent_instance


@router.post(
    "/analyze",
    response_model=DrugRepurposingResult,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    description="Perform comprehensive drug repurposing analysis using PubMed, PubChem, and ClinicalTrials.gov"
)
async def analyze_drug_repurposing(
    request: DrugRepurposingRequest,
    agent: DrugRepurposingAgent = Depends(get_agent)
):
    """
    Comprehensive drug repurposing analysis.
    
    Uses PubMed literature search, PubChem drug information, ClinicalTrials.gov,
    and web search to identify potential new therapeutic indications for existing drugs.
    """
    try:
        result = agent.analyze(request.drug_name, max_results=request.max_results)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
