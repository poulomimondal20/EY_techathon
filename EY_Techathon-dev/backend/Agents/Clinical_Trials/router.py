from fastapi import APIRouter, HTTPException
from .schemas import ClinicalTrialRequest, ClinicalTrialResponse, ClinicalTrialData
from .agent import ClinicalTrialAgent

router = APIRouter(
    prefix="/api/v1/clinical-trials",
    tags=["Clinical Trials"],
    responses={404: {"description": "Not found"}}
)

trial_agent = ClinicalTrialAgent()

@router.post("/analyze", response_model=ClinicalTrialResponse)
async def analyze_clinical_trials(request: ClinicalTrialRequest):
    """
    Analyze clinical trial pipeline for given drug/disease query.
    
    Parameters:
    - query: String containing the analysis request (e.g., "Analyze clinical trials for metformin in Alzheimer's")
    
    Returns:
    - Structured JSON analysis of clinical trial pipeline
    """
    try:
        result = trial_agent.analyze_drug_pipeline(request.query)
        return ClinicalTrialResponse(
            data=ClinicalTrialData(
                pipeline_summary=result.pipeline_summary,
                key_trials=result.key_trials,
                recent_updates=result.recent_updates,
                strategic_insights=result.strategic_insights
            ),
            status="success"
        )
    except Exception as e:
        return ClinicalTrialResponse(
            data=None,
            status="error",
            error=str(e)
        )