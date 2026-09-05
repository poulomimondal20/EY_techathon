"""
Medical Research Pipeline - Deep Research for Healthcare

A comprehensive agentic AI system for medical and pharmaceutical research,
combining Agno agents with LangGraph workflows for sophisticated research automation.

Features:
- Multi-agent architecture with specialized research agents
- LangGraph-based workflow orchestration
- PubMed literature search
- Clinical trials analysis
- Drug database integration
- Synthesis and gap analysis
- Quality critique and revision

Usage:
    from medical_research_pipeline import create_pipeline
    
    pipeline = create_pipeline()
    results = await pipeline.research("What are the latest treatments for Type 2 Diabetes?")
"""

from .orchestrator import (
    MedicalResearchPipeline,
    create_pipeline,
    run_research
)

from .config import (
    api_config,
    research_config,
    agent_config,
    APIConfig,
    ResearchConfig,
    AgentConfig
)

from .router import router

__version__ = "1.0.0"
__author__ = "Medical Research AI"

__all__ = [
    # Main classes
    "MedicalResearchPipeline",
    "create_pipeline",
    "run_research",
    
    # Configuration
    "api_config",
    "research_config", 
    "agent_config",
    "APIConfig",
    "ResearchConfig",
    "AgentConfig",
    
    # Router
    "router"
]
