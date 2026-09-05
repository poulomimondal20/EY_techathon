import os
import sys
import httpx
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import json

load_dotenv()


# ============== Output Schemas ==============

class SimilarDrug(BaseModel):
    """Schema for a similar drug found during analysis"""
    drug_name: str = Field(..., description="Name of the similar drug")
    current_indication: str = Field(..., description="Current approved indication/use of the drug")
    similarity_score: float = Field(..., description="Structural similarity score (0-1)", ge=0, le=1)
    mechanism_of_action: Optional[str] = Field(None, description="Mechanism of action if known")


class RepurposingCandidate(BaseModel):
    """Schema for a repurposing candidate prediction"""
    predicted_indication: str = Field(..., description="Predicted new therapeutic indication")
    confidence_score: float = Field(..., description="Confidence score for this prediction (0-1)", ge=0, le=1)
    evidence_strength: str = Field(..., description="Evidence strength: High, Medium, or Low")
    supporting_evidence: List[str] = Field(default_factory=list, description="List of supporting evidence points")
    similar_approved_drugs: List[str] = Field(default_factory=list, description="Similar drugs already approved for this indication")


class DrugProfile(BaseModel):
    """Schema for the drug being analyzed"""
    drug_name: str = Field(..., description="Name of the drug")
    smiles: Optional[str] = Field(None, description="SMILES structure of the drug")
    original_indication: Optional[str] = Field(None, description="Original approved indication")
    drug_class: Optional[str] = Field(None, description="Drug class/category")
    mechanism_of_action: Optional[str] = Field(None, description="Known mechanism of action")


class DrugRepurposingResult(BaseModel):
    """Main output schema for drug repurposing analysis"""
    summary: str = Field(..., description="Executive summary of the repurposing analysis")
    drug_profile: DrugProfile = Field(..., description="Profile of the analyzed drug")
    repurposing_candidates: List[RepurposingCandidate] = Field(
        default_factory=list, 
        description="List of potential repurposing candidates ranked by confidence"
    )
    similar_drugs: List[SimilarDrug] = Field(
        default_factory=list, 
        description="List of structurally similar drugs that informed the analysis"
    )
    clinical_considerations: List[str] = Field(
        default_factory=list, 
        description="Clinical considerations for repurposing (safety, dosing, etc.)"
    )
    research_gaps: List[str] = Field(
        default_factory=list, 
        description="Identified gaps requiring further research"
    )
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Strategic recommendations for drug repurposing"
    )
    data_sources: List[str] = Field(
        default_factory=list, 
        description="Data sources used in the analysis"
    )


class DrugRepurposingAgent:
    """
    Drug Repurposing Agent using Agno with Gemini.
    
    This agent analyzes drugs for potential new therapeutic indications
    using PubMed literature search and web search for evidence gathering.
    """
    
    def __init__(self):
        # Build tools list with web search and custom PubMed/drug info tools
        tools = [
            TavilyTools(), 
            ReasoningTools(),
            self._search_pubmed,
            self._get_drug_info_from_pubchem,
            self._search_clinical_trials,
        ]
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are an expert pharmaceutical scientist specializing in drug repurposing 
            and repositioning strategies. Your expertise includes:
            
            Core Expertise:
            - Identifying new therapeutic indications for existing drugs
            - Analyzing scientific literature for repurposing evidence
            - Understanding mechanism-based drug repurposing
            - Evaluating clinical evidence for off-label uses
            - Assessing safety and efficacy for new indications
            
            Your Analysis Approach:
            1. Search PubMed for literature on the drug and potential new uses
            2. Get drug information from PubChem (structure, properties, known uses)
            3. Search clinical trials for ongoing repurposing studies
            4. Use web search to find recent research on repurposing opportunities
            5. Synthesize all findings into a comprehensive analysis
            
            IMPORTANT: Always return your final response as valid JSON matching the DrugRepurposingResult schema.
            Do not include markdown formatting or extra text outside the JSON.""",
            tools=tools,
            markdown=False,
        )
    
    def _search_pubmed(self, query: str, max_results: int = 15) -> dict:
        """
        Search PubMed for scientific literature related to drug repurposing.
        
        Args:
            query: Search query (e.g., "metformin cancer repurposing")
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing PubMed search results
        """
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            # Search for article IDs
            search_url = f"{base_url}esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json"
            }
            
            response = httpx.get(search_url, params=search_params, timeout=30)
            search_data = response.json()
            
            if "esearchresult" not in search_data or not search_data["esearchresult"]["idlist"]:
                return {"error": "No results found", "query": query}
            
            # Get article details
            id_list = ",".join(search_data["esearchresult"]["idlist"])
            summary_url = f"{base_url}esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": id_list,
                "retmode": "json"
            }
            
            summary_response = httpx.get(summary_url, params=summary_params, timeout=30)
            summary_data = summary_response.json()
            
            articles = []
            for uid, article in summary_data["result"].items():
                if uid != "uids":
                    authors = article.get("authors", [])
                    author_names = [a.get("name", "") for a in authors[:3]] if authors else []
                    articles.append({
                        "pmid": article.get("uid"),
                        "title": article.get("title", ""),
                        "authors": author_names,
                        "journal": article.get("fulljournalname", ""),
                        "pubdate": article.get("pubdate", ""),
                    })
            
            return {
                "query": query,
                "total_results": len(articles),
                "articles": articles
            }
            
        except Exception as e:
            return {"error": f"PubMed search failed: {str(e)}", "query": query}
    
    def _get_drug_info_from_pubchem(self, drug_name: str) -> dict:
        """
        Get drug information from PubChem database.
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Dictionary containing drug information from PubChem
        """
        try:
            # Search for compound by name
            search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/JSON"
            response = httpx.get(search_url, timeout=30)
            
            if response.status_code != 200:
                return {"error": f"Drug '{drug_name}' not found in PubChem"}
            
            data = response.json()
            compound = data.get("PC_Compounds", [{}])[0]
            
            # Extract useful properties
            props = compound.get("props", [])
            properties = {}
            for prop in props:
                urn = prop.get("urn", {})
                label = urn.get("label", "")
                value = prop.get("value", {})
                if label in ["IUPAC Name", "Molecular Formula", "Molecular Weight", "SMILES", "InChI"]:
                    properties[label] = value.get("sval") or value.get("fval") or value.get("ival")
            
            cid = compound.get("id", {}).get("id", {}).get("cid")
            
            # Get additional description/pharmacology
            if cid:
                try:
                    desc_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
                    desc_response = httpx.get(desc_url, timeout=30)
                    if desc_response.status_code == 200:
                        desc_data = desc_response.json()
                        descriptions = desc_data.get("InformationList", {}).get("Information", [])
                        for desc in descriptions:
                            if desc.get("Description"):
                                properties["Description"] = desc.get("Description")[:500]
                                break
                except:
                    pass
            
            return {
                "drug_name": drug_name,
                "cid": cid,
                "properties": properties
            }
            
        except Exception as e:
            return {"error": f"PubChem lookup failed: {str(e)}"}
    
    def _search_clinical_trials(self, drug_name: str, max_results: int = 10) -> dict:
        """
        Search ClinicalTrials.gov for ongoing trials related to drug repurposing.
        
        Args:
            drug_name: Name of the drug
            max_results: Maximum number of results
            
        Returns:
            Dictionary containing clinical trial information
        """
        try:
            # Use ClinicalTrials.gov API v2
            url = "https://clinicaltrials.gov/api/v2/studies"
            params = {
                "query.intr": drug_name,
                "pageSize": max_results,
                "format": "json"
            }
            
            response = httpx.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                return {"error": "Clinical trials search failed"}
            
            data = response.json()
            studies = data.get("studies", [])
            
            trials = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                conditions_module = protocol.get("conditionsModule", {})
                
                trials.append({
                    "nct_id": id_module.get("nctId"),
                    "title": id_module.get("briefTitle"),
                    "status": status_module.get("overallStatus"),
                    "conditions": conditions_module.get("conditions", [])[:5],
                    "phase": protocol.get("designModule", {}).get("phases", [])
                })
            
            return {
                "drug_name": drug_name,
                "total_trials": len(trials),
                "trials": trials
            }
            
        except Exception as e:
            return {"error": f"Clinical trials search failed: {str(e)}"}
    
    def analyze(self, drug_name: str, max_results: int = 15) -> DrugRepurposingResult:
        """
        Perform comprehensive drug repurposing analysis.
        
        Args:
            drug_name: Name of the drug to analyze for repurposing
            max_results: Maximum number of literature results to consider
            
        Returns:
            DrugRepurposingResult containing the complete analysis
        """
        prompt = f"""Analyze the drug "{drug_name}" for potential repurposing opportunities.

        Please perform the following steps:
        1. Use the get_drug_info_from_pubchem tool to get drug information (structure, properties)
        2. Use the search_pubmed tool to find literature on "{drug_name} repurposing" and "{drug_name} new therapeutic indication"
        3. Use the search_clinical_trials tool to find ongoing trials for this drug
        4. Use web search (Tavily) to find recent news and research on repurposing opportunities
        5. Synthesize all findings into a comprehensive analysis
        
        Return your analysis as a JSON object with the following structure:
        {{
            "summary": "Executive summary of repurposing analysis",
            "drug_profile": {{
                "drug_name": "{drug_name}",
                "smiles": "SMILES if available from PubChem",
                "original_indication": "Original approved use",
                "drug_class": "Drug class",
                "mechanism_of_action": "MOA"
            }},
            "repurposing_candidates": [
                {{
                    "predicted_indication": "New indication",
                    "confidence_score": 0.85,
                    "evidence_strength": "High/Medium/Low",
                    "supporting_evidence": ["Evidence 1", "Evidence 2"],
                    "similar_approved_drugs": ["Drug1", "Drug2"]
                }}
            ],
            "similar_drugs": [
                {{
                    "drug_name": "Similar drug name",
                    "current_indication": "Current use",
                    "similarity_score": 0.9,
                    "mechanism_of_action": "MOA if known"
                }}
            ],
            "clinical_considerations": ["Consideration 1", "Consideration 2"],
            "research_gaps": ["Gap 1", "Gap 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "data_sources": ["PubMed", "ClinicalTrials.gov", "PubChem", "Web Search"]
        }}
        
        Base confidence scores on the strength of evidence found in literature and clinical trials.
        Provide actionable insights."""
        
        try:
            response = self.agent.run(prompt)
            
            # Parse the response
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Clean up the response if needed
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result_dict = json.loads(response_text.strip())
            return DrugRepurposingResult(**result_dict)
            
        except json.JSONDecodeError as e:
            # Return a basic result if JSON parsing fails
            return DrugRepurposingResult(
                summary=f"Analysis completed for {drug_name} but response parsing failed: {str(e)}",
                drug_profile=DrugProfile(drug_name=drug_name),
                recommendations=["Please retry the analysis"]
            )
        except Exception as e:
            return DrugRepurposingResult(
                summary=f"Analysis failed for {drug_name}: {str(e)}",
                drug_profile=DrugProfile(drug_name=drug_name),
                recommendations=["Please check the drug name and retry"]
            )
    
    def quick_predict(self, drug_name: str) -> dict:
        """
        Quick analysis using PubChem and PubMed without full web search.
        
        Args:
            drug_name: Name of the drug to analyze
            
        Returns:
            Dictionary with quick prediction results
        """
        drug_info = self._get_drug_info_from_pubchem(drug_name)
        pubmed_results = self._search_pubmed(f"{drug_name} repurposing drug repositioning", max_results=10)
        clinical_trials = self._search_clinical_trials(drug_name, max_results=5)
        
        return {
            "drug_name": drug_name,
            "drug_info": drug_info,
            "literature": pubmed_results,
            "clinical_trials": clinical_trials
        }


if __name__ == "__main__":
    print("Initializing Drug Repurposing Agent...")
    agent = DrugRepurposingAgent()
    
    test_drug = "Metformin"
    print(f"\n🔬 Analyzing drug: {test_drug}")
    
    # Quick analysis
    # quick_result = agent.quick_predict(test_drug)
    # print(json.dumps(quick_result, indent=2))
    
    print("\n Full Analysis:")
    full_result = agent.analyze(test_drug)
    print(full_result.model_dump_json(indent=2))