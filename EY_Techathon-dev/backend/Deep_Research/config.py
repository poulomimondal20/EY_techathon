import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class APIConfig:    
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    openrouter_api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    pubmed_api_key: str = field(default_factory=lambda: os.getenv("PUBMED_API_KEY", ""))
    serper_api_key: str = field(default_factory=lambda: os.getenv("SERPER_API_KEY", ""))
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    
    # Model configurations (Gemini)
    primary_model: str = "gemini-2.0-flash"
    reasoning_model: str = "gemini-2.0-flash"
    fast_model: str = "gemini-2.0-flash"
    embedding_model: str = "text-embedding-004"


@dataclass
class ResearchConfig:    
    max_papers_per_query: int = 20
    max_clinical_trials: int = 15
    max_drug_interactions: int = 10
    search_depth: str = "comprehensive"  # "quick", "standard", "comprehensive"
    include_preprints: bool = True
    include_clinical_trials: bool = True
    include_drug_databases: bool = True
    include_genomic_data: bool = False
    
    # Quality filters
    min_citation_count: int = 5
    max_publication_age_years: int = 10
    preferred_journals: list = field(default_factory=lambda: [
        "Nature Medicine",
        "The Lancet",
        "New England Journal of Medicine",
        "JAMA",
        "BMJ",
        "Cell",
        "Science",
        "Nature"
    ])


@dataclass
class AgentConfig:    
    max_iterations: int = 10
    timeout_seconds: int = 300
    enable_reflection: bool = True
    enable_critique: bool = True
    parallel_execution: bool = True
    memory_type: str = "buffer"  # "buffer", "summary", "vector"
    memory_k: int = 10


api_config = APIConfig()
research_config = ResearchConfig()
agent_config = AgentConfig()
