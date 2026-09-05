from pydantic import BaseModel, Field
from datetime import datetime


class WebSearchRequest(BaseModel):
    """Request schema for web search"""
    query: str = Field(..., description="Search query or research question", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Latest developments in artificial intelligence 2024"
            }
        }


class WebSearchResponse(BaseModel):
    """Response schema for web search"""
    query: str
    status: str = Field(..., description="Status: success or error")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    search_results: str = Field(..., description="Comprehensive search results with sources")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Latest developments in artificial intelligence 2024",
                "status": "success",
                "timestamp": "2024-01-15T10:30:00",
                "search_results": "Comprehensive research findings with sources..."
            }
        }
