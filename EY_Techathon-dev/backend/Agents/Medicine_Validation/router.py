from fastapi import APIRouter, HTTPException, status
from .agent import MedicineValidationAgent
from .schemas import MedicineValidationRequest, MedicineValidationResponse, MedicineValidationData
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/medicine-validation",
    tags=["Medicine Validation"]
)

_agent_instance = None


def get_agent() -> MedicineValidationAgent:
    """Get or create medicine validation agent instance"""
    global _agent_instance
    if _agent_instance is None:
        logger.info("Initializing Medicine Validation Agent...")
        _agent_instance = MedicineValidationAgent()
    return _agent_instance


@router.post(
    "/validate",
    response_model=MedicineValidationResponse,
    summary="Validate medicine with structured response",
    description="Comprehensive medicine validation including FDA status and safety profile"
)
async def validate_medicine(request: MedicineValidationRequest) -> MedicineValidationResponse:
    """
    Validate a medicine with comprehensive analysis.
    
    Returns structured JSON validation report.
    """
    try:
        logger.info(f"Validating medicine: {request.medicine_name}")
        
        agent = get_agent()
        result = agent.validate_drug(request.medicine_name)
        
        response = MedicineValidationResponse(
            data=MedicineValidationData(
                medicine_name=result.medicine_name,
                is_approved=result.is_approved,
                regulatory_status=result.regulatory_status,
                approved_indications=result.approved_indications,
                safety_warnings=result.safety_warnings,
                manufacturers=result.manufacturers,
                prescription_status=result.prescription_status,
                summary=result.summary
            ),
            status="success",
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Successfully validated medicine: {request.medicine_name}")
        return response
        
    except Exception as e:
        logger.error(f"Error validating medicine {request.medicine_name}: {str(e)}")
        return MedicineValidationResponse(
            data=None,
            status="error",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )
