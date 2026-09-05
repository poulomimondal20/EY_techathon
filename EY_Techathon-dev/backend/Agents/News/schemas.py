from typing import Optional, List
from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    title: str = Field(..., description="Headline title")
    description: Optional[str] = Field(None, description="Short summary")
    url: str = Field(..., description="Source URL")
    source: str = Field(..., description="Publisher/source name")
    published_at: str = Field(..., description="ISO timestamp")
    image_url: Optional[str] = Field(None, description="Thumbnail image URL")


class NewsResponse(BaseModel):
    status: str = Field("success", description="Request status")
    total_results: int = Field(0, description="Number of returned articles")
    articles: List[NewsArticle] = Field(default_factory=list)


class NewsQueryRequest(BaseModel):
    topic: str = Field("medicine", description="Topic or keywords to search for")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    language: str = Field("en")
