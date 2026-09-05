"""
ESG Report Generator Router
Provides API endpoints for ESG report generation and PDF download
"""

import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .agent import generate_esg_report
from .pdf_generator import ESGReportPDFGenerator

router = APIRouter(prefix="/api/v1/esg", tags=["ESG Report Generator"])


class ESGReportRequest(BaseModel):
    """Request model for ESG report generation"""
    company_name: str
    industry: Optional[str] = None
    reporting_period: str = "2024"


class ESGReportResponse(BaseModel):
    """Response model for ESG report generation"""
    success: bool
    company_name: str
    message: str
    pdf_filename: Optional[str] = None
    download_url: Optional[str] = None
    view_url: Optional[str] = None  # Direct link to view in browser
    scores: Optional[dict] = None
    timestamp: str


# Store for generated reports (in production, use a database)
generated_reports = {}


@router.post("/generate", response_model=ESGReportResponse)
async def generate_report(request: ESGReportRequest):
    """
    Generate a comprehensive ESG report for a company.
    Returns the report data and a download URL for the PDF.
    """
    try:
        # Generate the ESG report
        result = await generate_esg_report(
            company_name=request.company_name,
            industry=request.industry,
            reporting_period=request.reporting_period
        )
        
        if result.get("success"):
            pdf_path = result.get("pdf_path", "")
            pdf_filename = os.path.basename(pdf_path) if pdf_path else None
            
            # Store report reference
            if pdf_filename:
                generated_reports[pdf_filename] = {
                    "path": pdf_path,
                    "company": request.company_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            return ESGReportResponse(
                success=True,
                company_name=request.company_name,
                message="ESG report generated successfully",
                pdf_filename=pdf_filename,
                download_url=f"/api/v1/esg/download/{pdf_filename}" if pdf_filename else None,
                view_url=f"/api/v1/esg/download/{pdf_filename}" if pdf_filename else None,  # Direct clickable link
                scores=result.get("calculated_scores"),
                timestamp=result.get("timestamp", datetime.now().isoformat())
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download a generated ESG report PDF.
    """
    # Get report directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    project_dir = os.path.dirname(backend_dir)
    reports_dir = os.path.join(project_dir, "reports")
    
    # Construct file path
    file_path = os.path.join(reports_dir, filename)
    
    # Security check - ensure file is in reports directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(reports_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/reports")
async def list_reports():
    """
    List all available ESG reports for download.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    project_dir = os.path.dirname(backend_dir)
    reports_dir = os.path.join(project_dir, "reports")
    
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    reports = []
    for filename in os.listdir(reports_dir):
        if filename.endswith(".pdf") and filename.startswith("ESG_Report_"):
            file_path = os.path.join(reports_dir, filename)
            stat = os.stat(file_path)
            
            # Extract company name from filename
            parts = filename.replace("ESG_Report_", "").replace(".pdf", "").rsplit("_", 2)
            company_name = parts[0].replace("_", " ") if parts else "Unknown"
            
            reports.append({
                "filename": filename,
                "company_name": company_name,
                "download_url": f"/esg/download/{filename}",
                "size_kb": round(stat.st_size / 1024, 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"reports": reports}


@router.delete("/reports/{filename}")
async def delete_report(filename: str):
    """
    Delete a specific ESG report.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    project_dir = os.path.dirname(backend_dir)
    reports_dir = os.path.join(project_dir, "reports")
    
    file_path = os.path.join(reports_dir, filename)
    
    # Security check
    if not os.path.abspath(file_path).startswith(os.path.abspath(reports_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        os.remove(file_path)
        return {"success": True, "message": f"Report {filename} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
