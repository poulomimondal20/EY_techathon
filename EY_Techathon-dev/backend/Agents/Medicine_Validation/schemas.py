from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MedicineValidationRequest(BaseModel):
    """Request schema for medicine validation"""
    medicine_name: str = Field(..., description="Name of the medicine to validate", min_length=1)


class MedicineValidationData(BaseModel):
    """Structured medicine validation data"""
    medicine_name: str = Field(..., description="Name of the validated medicine")
    is_approved: bool = Field(..., description="Whether the medicine is FDA approved")
    regulatory_status: str = Field(..., description="Current regulatory approval status")
    approved_indications: List[str] = Field(default_factory=list, description="Approved uses")
    safety_warnings: List[str] = Field(default_factory=list, description="Safety warnings")
    manufacturers: List[str] = Field(default_factory=list, description="Authorized manufacturers")
    prescription_status: str = Field(..., description="Prescription or OTC status")
    summary: str = Field(..., description="Brief validation summary")


class MedicineValidationResponse(BaseModel):
    """Response schema for medicine validation"""
    data: Optional[MedicineValidationData] = None
    status: str = "success"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None
