"""
ESG Report Generator Module
Multi-agent system for comprehensive ESG research and reporting
"""

__version__ = "1.0.0"
__author__ = "EY Tech"

try:
    from agent import generate_esg_report, conduct_esg_research
    from tools import (
        tavily_web_search,
        search_environmental_data,
        search_social_data,
        search_governance_data,
        search_esg_news,
        search_esg_reports,
    )
except ImportError:
    pass

__all__ = [
    "generate_esg_report",
    "conduct_esg_research",
    "tavily_web_search",
    "search_environmental_data",
    "search_social_data",
    "search_governance_data",
    "search_esg_news",
    "search_esg_reports",
]
