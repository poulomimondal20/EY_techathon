"""
Research Tools for Medical/Pharmaceutical Research Pipeline.

This module contains specialized tools for:
- PubMed/Medical Literature Search
- Clinical Trials Search
- Drug Database Queries
- FDA/EMA Database Access
- Genomic Data Access
- Web Search for Latest Research
"""

import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field


# ============================================================================
# Data Models
# ============================================================================

class PaperResult(BaseModel):
    """Structured result for a research paper."""
    
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: Optional[int] = None
    url: Optional[str] = None
    full_text_available: bool = False


class ClinicalTrialResult(BaseModel):
    """Structured result for a clinical trial."""
    
    nct_id: str
    title: str
    status: str
    phase: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)
    sponsor: Optional[str] = None
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    enrollment: Optional[int] = None
    primary_outcomes: List[str] = Field(default_factory=list)
    url: Optional[str] = None


class DrugInfo(BaseModel):
    """Structured drug information."""
    
    name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = Field(default_factory=list)
    drug_class: Optional[str] = None
    mechanism: Optional[str] = None
    indications: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)
    interactions: List[str] = Field(default_factory=list)
    fda_status: Optional[str] = None
    approval_date: Optional[str] = None


class ResearchContext(BaseModel):
    """Context object for research queries."""
    
    query: str
    domain: str = "general"  # "oncology", "cardiology", "neurology", etc.
    research_type: str = "comprehensive"
    papers: List[PaperResult] = Field(default_factory=list)
    clinical_trials: List[ClinicalTrialResult] = Field(default_factory=list)
    drugs: List[DrugInfo] = Field(default_factory=list)
    synthesis: Optional[str] = None
    gaps_identified: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ============================================================================
# Base Tool Class
# ============================================================================

class BaseTool(ABC):
    """Base class for all research tools."""
    
    name: str = "base_tool"
    description: str = "Base tool class"
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters."""
        pass


# ============================================================================
# PubMed Search Tool
# ============================================================================

class PubMedSearchTool(BaseTool):
    """Tool for searching PubMed medical literature database."""
    
    name = "pubmed_search"
    description = """Search PubMed for medical research papers. 
    Use this for finding peer-reviewed medical literature, clinical studies, 
    and scientific articles on diseases, treatments, drugs, and medical conditions."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for PubMed"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                },
                "date_range": {
                    "type": "string",
                    "description": "Date range filter (e.g., '2020:2024')",
                    "default": None
                },
                "article_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by article types (e.g., 'Clinical Trial', 'Review')"
                }
            },
            "required": ["query"]
        }
    
    async def execute(
        self, 
        query: str, 
        max_results: int = 10,
        date_range: Optional[str] = None,
        article_types: Optional[List[str]] = None
    ) -> List[PaperResult]:
        """Search PubMed and return structured paper results."""
        
        # Build search query with filters
        search_query = query
        if date_range:
            search_query += f" AND {date_range}[dp]"
        if article_types:
            type_filter = " OR ".join([f'"{t}"[pt]' for t in article_types])
            search_query += f" AND ({type_filter})"
        
        # Search for IDs
        search_params = {
            "db": "pubmed",
            "term": search_query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        if self.api_key:
            search_params["api_key"] = self.api_key
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get PMIDs
            search_response = await client.get(
                f"{self.base_url}/esearch.fcgi",
                params=search_params
            )
            search_data = search_response.json()
            
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []
            
            # Fetch paper details
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "rettype": "abstract"
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key
                
            fetch_response = await client.get(
                f"{self.base_url}/efetch.fcgi",
                params=fetch_params
            )
            
            return self._parse_pubmed_xml(fetch_response.text, pmids)
    
    def _parse_pubmed_xml(self, xml_text: str, pmids: List[str]) -> List[PaperResult]:
        """Parse PubMed XML response into structured results."""
        results = []
        
        # Simple regex-based parsing (for production, use proper XML parser)
        for pmid in pmids:
            try:
                # Extract title
                title_match = re.search(
                    rf'<PubmedArticle>.*?<PMID[^>]*>{pmid}</PMID>.*?<ArticleTitle>(.*?)</ArticleTitle>',
                    xml_text, re.DOTALL
                )
                title = title_match.group(1) if title_match else "Unknown Title"
                title = re.sub(r'<[^>]+>', '', title)  # Remove XML tags
                
                # Extract abstract
                abstract_match = re.search(
                    rf'<PMID[^>]*>{pmid}</PMID>.*?<AbstractText[^>]*>(.*?)</AbstractText>',
                    xml_text, re.DOTALL
                )
                abstract = abstract_match.group(1) if abstract_match else None
                if abstract:
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                
                # Extract journal
                journal_match = re.search(
                    rf'<PMID[^>]*>{pmid}</PMID>.*?<Title>(.*?)</Title>',
                    xml_text, re.DOTALL
                )
                journal = journal_match.group(1) if journal_match else None
                
                results.append(PaperResult(
                    pmid=pmid,
                    title=title,
                    abstract=abstract,
                    journal=journal,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                ))
            except Exception:
                continue
                
        return results


# ============================================================================
# Clinical Trials Search Tool
# ============================================================================

class ClinicalTrialsSearchTool(BaseTool):
    """Tool for searching ClinicalTrials.gov database."""
    
    name = "clinical_trials_search"
    description = """Search ClinicalTrials.gov for ongoing and completed clinical trials.
    Use this to find information about drug trials, treatment studies, and experimental therapies."""
    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for clinical trials"
                },
                "condition": {
                    "type": "string",
                    "description": "Disease or condition to search for"
                },
                "intervention": {
                    "type": "string", 
                    "description": "Treatment or intervention to search for"
                },
                "status": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Trial status filter (e.g., 'RECRUITING', 'COMPLETED')"
                },
                "phase": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Trial phase filter (e.g., 'PHASE3', 'PHASE4')"
                },
                "max_results": {
                    "type": "integer",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    
    async def execute(
        self,
        query: str,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        status: Optional[List[str]] = None,
        phase: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[ClinicalTrialResult]:
        """Search clinical trials and return structured results."""
        
        params = {
            "query.term": query,
            "pageSize": max_results,
            "format": "json"
        }
        
        if condition:
            params["query.cond"] = condition
        if intervention:
            params["query.intr"] = intervention
        if status:
            params["filter.overallStatus"] = ",".join(status)
        if phase:
            params["filter.phase"] = ",".join(phase)
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
        return self._parse_trials(data)
    
    def _parse_trials(self, data: Dict) -> List[ClinicalTrialResult]:
        """Parse clinical trials API response."""
        results = []
        studies = data.get("studies", [])
        
        for study in studies:
            try:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})
                conditions_module = protocol.get("conditionsModule", {})
                interventions_module = protocol.get("armsInterventionsModule", {})
                outcomes_module = protocol.get("outcomesModule", {})
                sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
                
                # Extract interventions
                interventions = []
                for intr in interventions_module.get("interventions", []):
                    interventions.append(f"{intr.get('type', '')}: {intr.get('name', '')}")
                
                # Extract primary outcomes
                primary_outcomes = []
                for outcome in outcomes_module.get("primaryOutcomes", []):
                    primary_outcomes.append(outcome.get("measure", ""))
                
                results.append(ClinicalTrialResult(
                    nct_id=id_module.get("nctId", ""),
                    title=id_module.get("briefTitle", ""),
                    status=status_module.get("overallStatus", ""),
                    phase=",".join(design_module.get("phases", [])),
                    conditions=conditions_module.get("conditions", []),
                    interventions=interventions,
                    sponsor=sponsor_module.get("leadSponsor", {}).get("name"),
                    start_date=status_module.get("startDateStruct", {}).get("date"),
                    completion_date=status_module.get("completionDateStruct", {}).get("date"),
                    enrollment=design_module.get("enrollmentInfo", {}).get("count"),
                    primary_outcomes=primary_outcomes,
                    url=f"https://clinicaltrials.gov/study/{id_module.get('nctId', '')}"
                ))
            except Exception:
                continue
                
        return results


# ============================================================================
# Drug Database Tool
# ============================================================================

class DrugDatabaseTool(BaseTool):
    """Tool for querying drug databases (OpenFDA, DrugBank concepts)."""
    
    name = "drug_database"
    description = """Query drug databases for medication information including 
    indications, contraindications, side effects, interactions, and FDA approval status."""
    
    def __init__(self):
        self.openfda_url = "https://api.fda.gov/drug"
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "drug_name": {
                    "type": "string",
                    "description": "Name of the drug to search for"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["label", "adverse_events", "recalls", "ndc"],
                    "description": "Type of drug information to retrieve",
                    "default": "label"
                }
            },
            "required": ["drug_name"]
        }
    
    async def execute(
        self,
        drug_name: str,
        query_type: str = "label"
    ) -> List[DrugInfo]:
        """Query drug database and return structured results."""
        
        endpoint_map = {
            "label": "/label.json",
            "adverse_events": "/event.json",
            "recalls": "/enforcement.json",
            "ndc": "/ndc.json"
        }
        
        endpoint = endpoint_map.get(query_type, "/label.json")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
                "limit": 5
            }
            
            response = await client.get(
                f"{self.openfda_url}{endpoint}",
                params=params
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            
        return self._parse_drug_labels(data, drug_name)
    
    def _parse_drug_labels(self, data: Dict, query_name: str) -> List[DrugInfo]:
        """Parse OpenFDA drug label response."""
        results = []
        
        for result in data.get("results", []):
            try:
                openfda = result.get("openfda", {})
                
                # Extract indications
                indications = []
                if "indications_and_usage" in result:
                    indications = result["indications_and_usage"][:3]
                
                # Extract contraindications
                contraindications = []
                if "contraindications" in result:
                    contraindications = result["contraindications"][:3]
                
                # Extract side effects
                side_effects = []
                if "adverse_reactions" in result:
                    side_effects = result["adverse_reactions"][:3]
                
                # Extract interactions
                interactions = []
                if "drug_interactions" in result:
                    interactions = result["drug_interactions"][:3]
                
                results.append(DrugInfo(
                    name=query_name,
                    generic_name=openfda.get("generic_name", [None])[0] if openfda.get("generic_name") else None,
                    brand_names=openfda.get("brand_name", []),
                    drug_class=openfda.get("pharm_class_epc", [None])[0] if openfda.get("pharm_class_epc") else None,
                    mechanism=openfda.get("pharm_class_moa", [None])[0] if openfda.get("pharm_class_moa") else None,
                    indications=indications,
                    contraindications=contraindications,
                    side_effects=side_effects,
                    interactions=interactions,
                    fda_status="Approved" if openfda else "Unknown"
                ))
            except Exception:
                continue
                
        return results


# ============================================================================
# Web Search Tool (Using Tavily/Serper)
# ============================================================================

class WebSearchTool(BaseTool):
    """Tool for searching the web for latest medical research news and information."""
    
    name = "web_search"
    description = """Search the web for recent medical research news, articles, 
    and information not yet in academic databases. Good for finding latest developments."""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "tavily"):
        self.api_key = api_key
        self.provider = provider
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "max_results": {
                    "type": "integer",
                    "default": 10
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "default": "advanced"
                }
            },
            "required": ["query"]
        }
    
    async def execute(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced"
    ) -> List[Dict[str, Any]]:
        """Search the web and return results."""
        
        if self.provider == "tavily":
            return await self._search_tavily(query, max_results, search_depth)
        else:
            return await self._search_serper(query, max_results)
    
    async def _search_tavily(
        self, query: str, max_results: int, search_depth: str
    ) -> List[Dict[str, Any]]:
        """Search using Tavily API."""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": f"medical research {query}",
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_domains": [
                        "nih.gov", "ncbi.nlm.nih.gov", "nature.com",
                        "sciencedirect.com", "thelancet.com", "nejm.org",
                        "jamanetwork.com", "bmj.com", "cell.com"
                    ]
                }
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            
        return data.get("results", [])
    
    async def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Serper API."""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key},
                json={
                    "q": f"medical research {query}",
                    "num": max_results
                }
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            
        return data.get("organic", [])


# ============================================================================
# Literature Synthesis Tool
# ============================================================================

class LiteratureSynthesisTool(BaseTool):    
    name = "synthesize_literature"
    description = """Analyze and synthesize a collection of research papers to 
    identify trends, consensus, contradictions, and research gaps."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of paper results to synthesize"
                },
                "focus_area": {
                    "type": "string",
                    "description": "Specific aspect to focus synthesis on"
                },
                "synthesis_type": {
                    "type": "string",
                    "enum": ["overview", "comparative", "gap_analysis", "meta_summary"],
                    "default": "overview"
                }
            },
            "required": ["papers"]
        }
    
    async def execute(
        self,
        papers: List[Dict],
        focus_area: Optional[str] = None,
        synthesis_type: str = "overview"
    ) -> Dict[str, Any]:
        
        # Prepare papers for synthesis
        paper_summaries = []
        for paper in papers[:20]:  # Limit to 20 papers
            summary = {
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", "")[:500] if paper.get("abstract") else "",
                "journal": paper.get("journal", ""),
                "pmid": paper.get("pmid", "")
            }
            paper_summaries.append(summary)
        
        synthesis_prompt = self._build_synthesis_prompt(
            paper_summaries, focus_area, synthesis_type
        )
        
        # If LLM client available, use it for synthesis
        if self.llm_client:
            response = await self._llm_synthesis(synthesis_prompt)
            return {"synthesis": response, "papers_analyzed": len(paper_summaries)}
        
        return {
            "synthesis_type": synthesis_type,
            "focus_area": focus_area,
            "papers_analyzed": len(paper_summaries),
            "paper_summaries": paper_summaries,
            "note": "LLM synthesis not available - returning raw summaries"
        }
    
    def _build_synthesis_prompt(
        self, papers: List[Dict], focus_area: Optional[str], synthesis_type: str
    ) -> str:
        """Build prompt for literature synthesis."""
        
        papers_text = "\n\n".join([
            f"Paper {i+1}:\nTitle: {p['title']}\nJournal: {p['journal']}\nAbstract: {p['abstract']}"
            for i, p in enumerate(papers)
        ])
        
        prompts = {
            "overview": f"""Synthesize the following medical research papers into a comprehensive overview.
            
Papers:
{papers_text}

Provide:
1. Main findings and themes
2. Consensus in the literature
3. Key methodologies used
4. Important conclusions""",
            
            "comparative": f"""Compare and contrast the following medical research papers.

Papers:
{papers_text}

Focus area: {focus_area or 'General comparison'}

Provide:
1. Similarities in findings
2. Contradictions or disagreements
3. Methodological differences
4. Strength of evidence for each position""",
            
            "gap_analysis": f"""Analyze the following medical research papers to identify research gaps.

Papers:
{papers_text}

Provide:
1. Topics well-covered in current research
2. Identified gaps in the literature
3. Unanswered questions
4. Recommendations for future research""",
            
            "meta_summary": f"""Create a meta-summary of the following medical research papers.

Papers:
{papers_text}

Provide:
1. Executive summary (2-3 sentences)
2. Key statistics and numbers mentioned
3. Clinical implications
4. Level of evidence assessment"""
        }
        
        return prompts.get(synthesis_type, prompts["overview"])
    
    async def _llm_synthesis(self, prompt: str) -> str:
        # This would call the actual LLM
        return "LLM synthesis would be generated here"


# ============================================================================
# Tool Registry
# ============================================================================

class ToolRegistry:    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        
    def register(self, tool: BaseTool) -> None:
        self.tools[tool.name] = tool
        
    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return [tool.to_function_schema() for tool in self.tools.values()]


def create_default_tool_registry(
    pubmed_api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    serper_api_key: Optional[str] = None
) -> ToolRegistry:    
    registry = ToolRegistry()
    
    # Register all tools
    registry.register(PubMedSearchTool(api_key=pubmed_api_key))
    registry.register(ClinicalTrialsSearchTool())
    registry.register(DrugDatabaseTool())
    registry.register(WebSearchTool(api_key=tavily_api_key or serper_api_key))
    registry.register(LiteratureSynthesisTool())
    
    return registry
