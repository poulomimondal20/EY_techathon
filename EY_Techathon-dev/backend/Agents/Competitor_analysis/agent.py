import os
import sys
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Initialize as None, will be set if imports succeed
ClinicalTrialsAPIClient = None
PatentSearchTool = None
search_pubmed_literature = None

try:
    from Tools.clinical_trial_tool import ClinicalTrialsAPIClient
    from Tools.literature_mining_tool import search_pubmed_literature
    from Tools.patent_search_tool import PatentSearchTool
except ImportError as e:
    print(f"Warning: Some tools not found: {e}")

load_dotenv()


class CompetitorProfile(BaseModel):
    name: str = Field(..., description="Competitor company name")
    market_share: Optional[str] = Field(None, description="Estimated market share percentage")
    revenue: Optional[str] = Field(None, description="Annual revenue in this segment")
    active_trials: Optional[int] = Field(None, description="Number of active clinical trials")
    pipeline_drugs: Optional[int] = Field(None, description="Number of drugs in pipeline")
    key_products: List[str] = Field(default_factory=list, description="Key products with sales figures")
    strengths: List[str] = Field(default_factory=list, description="Competitive strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Competitive weaknesses")

class CompetitorAnalysisResult(BaseModel):
    overview: str = Field(..., description="Executive summary of the competitive landscape")
    market_size: Optional[str] = Field(None, description="Total addressable market size")
    market_growth_rate: Optional[str] = Field(None, description="Annual growth rate (CAGR)")
    total_competitors: Optional[int] = Field(None, description="Number of major competitors")
    competitors: List[CompetitorProfile] = Field(default_factory=list, description="Detailed competitor profiles")
    pipeline_insights: List[str] = Field(default_factory=list, description="Pipeline insights with numbers")
    market_trends: List[str] = Field(default_factory=list, description="Key market trends with data")
    threats: List[str] = Field(default_factory=list, description="Competitive threats identified")
    opportunities: List[str] = Field(default_factory=list, description="Market opportunities with potential value")
    recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations")


class CompetitorAnalysisAgent:
    
    def __init__(self):
        self.trials_client = ClinicalTrialsAPIClient() if ClinicalTrialsAPIClient else None
        self.patent_tool = PatentSearchTool() if PatentSearchTool else None
        
        # Build tools list based on available tools
        tools = [TavilyTools(), ReasoningTools()]
        if self.trials_client:
            tools.extend([
                self._get_competitor_trials_wrapper,
                self._get_trial_details_wrapper,
                self._monitor_multiple_competitors_wrapper,
                self._analyze_competitor_pipeline_wrapper
            ])
        if self.patent_tool:
            tools.append(self._search_competitor_patents_wrapper)
        if search_pubmed_literature:
            tools.append(self._search_competitor_publications_wrapper)
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a pharmaceutical competitor intelligence analyst with expertise in 
            competitive landscape analysis, clinical trial monitoring, and strategic market positioning.
            
            Core Expertise:
            - Competitor clinical trial portfolio analysis
            - Patent landscape and IP intelligence
            - Market positioning and strategic assessment
            - Pipeline strength and opportunity identification
            
            RESPONSE FORMAT: Return your final response as valid JSON only, no markdown or extra text.""",
            tools=tools,
            markdown=False,
        )
    
    def _get_competitor_trials_wrapper(self, competitor_name: str, 
                                      status: str = None, 
                                      phase: str = None, 
                                      limit: int = 100):
        try:
            df = self.trials_client.get_trials_by_sponsor(
                sponsor_name=competitor_name,
                recruitment_status=status,
                phase=phase,
                limit=limit
            )
            
            if df.empty:
                return {
                    "competitor": competitor_name,
                    "total_trials": 0,
                    "message": "No trials found for this competitor",
                    "trials": []
                }
            
            trials_data = df.to_dict('records')            
            stats = {
                "total_trials": len(df),
                "by_status": df['status'].value_counts().to_dict() if 'status' in df.columns else {},
                "by_phase": df['phase'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown').value_counts().to_dict(),
                "total_enrollment": df['enrollment'].sum() if 'enrollment' in df.columns else 0,
                "conditions": df['condition'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown').value_counts().head(10).to_dict() if 'condition' in df.columns else {}
            }
            
            return {
                "competitor": competitor_name,
                "statistics": stats,
                "trials": trials_data[:20],  # Return first 20 trials
                "total_found": len(trials_data)
            }
        except Exception as e:
            return {"error": f"Failed to fetch trials: {str(e)}", "competitor": competitor_name}
    
    def _get_trial_details_wrapper(self, nct_id: str):
        try:
            details = self.trials_client.get_trial_details(nct_id)
            
            if not details:
                return {"error": "Trial not found", "nct_id": nct_id}
            
            # Extract key information
            protocol = details.get("protocolSection", {})
            
            trial_info = {
                "nct_id": nct_id,
                "title": protocol.get("identificationModule", {}).get("officialTitle", ""),
                "brief_summary": protocol.get("descriptionModule", {}).get("briefSummary", "")[:500],
                "status": protocol.get("statusModule", {}).get("overallStatus", ""),
                "phase": protocol.get("designModule", {}).get("phases", []),
                "enrollment": protocol.get("designModule", {}).get("enrollmentInfo", {}),
                "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
                "interventions": protocol.get("armsInterventionsModule", {}).get("interventions", []),
                "sponsor": protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}),
                "start_date": protocol.get("statusModule", {}).get("startDateStruct", {}),
                "completion_date": protocol.get("statusModule", {}).get("completionDateStruct", {})
            }
            
            return trial_info
        except Exception as e:
            return {"error": f"Failed to fetch trial details: {str(e)}", "nct_id": nct_id}
    
    def _monitor_multiple_competitors_wrapper(self, competitor_list: str):
        """Monitor trials across multiple competitors (comma-separated names)"""
        try:
            # Parse competitor list
            competitors = [c.strip() for c in competitor_list.split(',')]
            
            df = self.trials_client.monitor_competitor_trials(competitors)
            
            if df.empty:
                return {
                    "competitors": competitors,
                    "total_trials": 0,
                    "message": "No trials found",
                    "comparison": {}
                }
            
            # Comparative analysis
            comparison = {}
            for competitor in competitors:
                comp_df = df[df['sponsor'] == competitor]
                comparison[competitor] = {
                    "total_trials": len(comp_df),
                    "by_status": comp_df['status'].value_counts().to_dict() if not comp_df.empty else {},
                    "by_phase": comp_df['phase'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown').value_counts().to_dict() if not comp_df.empty else {},
                    "total_enrollment": int(comp_df['enrollment'].sum()) if 'enrollment' in comp_df.columns else 0
                }
            
            return {
                "competitors": competitors,
                "total_trials": len(df),
                "comparison": comparison,
                "all_trials": df.to_dict('records')[:30]  # Return first 30 trials
            }
        except Exception as e:
            return {"error": f"Failed to monitor competitors: {str(e)}"}
    
    def _search_competitor_patents_wrapper(self, competitor_name: str):
        """Search patents by competitor/assignee name"""
        try:
            results = self.patent_tool.search_by_keyword(f"{competitor_name} pharmaceutical drug")
            
            return {
                "competitor": competitor_name,
                "total_patents": len(results) if results else 0,
                "patents": results[:15] if results else [],
                "search_query": f"{competitor_name} pharmaceutical drug"
            }
        except Exception as e:
            return {"error": f"Patent search failed: {str(e)}", "competitor": competitor_name}
    
    def _search_competitor_publications_wrapper(self, competitor_topic: str, max_results: int = 20):
        """Search scientific publications related to competitor research"""
        try:
            results_json = search_pubmed_literature(competitor_topic, max_results)
            results = json.loads(results_json)
            
            return {
                "topic": competitor_topic,
                "publications": results
            }
        except Exception as e:
            return {"error": f"Publication search failed: {str(e)}", "topic": competitor_topic}
    
    def _analyze_competitor_pipeline_wrapper(self, competitor_name: str):
        """Comprehensive pipeline analysis for a competitor"""
        try:
            # Get all trials
            df = self.trials_client.get_trials_by_sponsor(competitor_name, limit=500)
            
            if df.empty:
                return {
                    "competitor": competitor_name,
                    "message": "No pipeline data found",
                    "analysis": {}
                }
            
            # Pipeline analysis
            analysis = {
                "competitor": competitor_name,
                "total_programs": len(df),
                "phase_distribution": df['phase'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown').value_counts().to_dict(),
                "status_distribution": df['status'].value_counts().to_dict(),
                "therapeutic_areas": df['condition'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown').value_counts().head(10).to_dict(),
                "total_patient_enrollment": int(df['enrollment'].sum()) if 'enrollment' in df.columns else 0,
                "active_trials": len(df[df['status'].isin(['RECRUITING', 'ACTIVE_NOT_RECRUITING', 'ENROLLING_BY_INVITATION'])]),
                "recent_starts": len(df[df['start_date'].notna()]) if 'start_date' in df.columns else 0,
                "key_programs": df.nlargest(10, 'enrollment')[['nct_id', 'title', 'phase', 'enrollment', 'condition']].to_dict('records') if 'enrollment' in df.columns else []
            }
            
            return analysis
        except Exception as e:
            return {"error": f"Pipeline analysis failed: {str(e)}", "competitor": competitor_name}
    
    def answer(self, query: str) -> CompetitorAnalysisResult:
        """Run competitor analysis based on natural language query"""
        try:
            result = self.agent.run(f"""
            Conduct comprehensive competitor analysis for: {query}
            
            Search for and analyze with SPECIFIC NUMBERS and DATA:
            - Market size (in $B), growth rate (CAGR %), and projections
            - Key competitors with market shares (%), revenue figures, trial counts
            - Pipeline data: number of trials by phase, drugs in development
            - Quantitative market trends with percentages and figures
            
            Return your response as a JSON object with this exact structure:
            {{
                "overview": "Executive summary with key numbers (market size, growth, top players)",
                "market_size": "$XXB (e.g., $50B)",
                "market_growth_rate": "X% CAGR (e.g., 8.5% CAGR 2024-2030)",
                "total_competitors": 5,
                "competitors": [
                    {{
                        "name": "Company Name",
                        "market_share": "XX%",
                        "revenue": "$X.XB in this segment",
                        "active_trials": 25,
                        "pipeline_drugs": 12,
                        "key_products": ["Product 1 ($XB sales)", "Product 2 ($XM sales)"],
                        "strengths": ["Strength with data"],
                        "weaknesses": ["Weakness with impact"]
                    }}
                ],
                "pipeline_insights": ["X drugs in Phase 3", "Y% success rate in trials"],
                "market_trends": ["Trend growing at X%", "Segment worth $XB by 2030"],
                "threats": ["Threat with quantified impact"],
                "opportunities": ["$XB opportunity in segment"],
                "recommendations": ["Action with expected ROI/impact"]
            }}
            
            Include specific numbers, percentages, dollar amounts wherever possible.
            Return ONLY the JSON object, no additional text or markdown.
            """).content
            
            if not result or result.strip() == "":
                return CompetitorAnalysisResult(
                    overview="Error: Unable to generate analysis",
                    recommendations=[]
                )
            
            # Clean up the response
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.startswith("```"):
                cleaned_result = cleaned_result[3:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()
            
            data = json.loads(cleaned_result)
            return CompetitorAnalysisResult(**data)
            
        except json.JSONDecodeError as e:
            return CompetitorAnalysisResult(
                overview=f"Error parsing response: {str(e)}",
                recommendations=[]
            )
        except Exception as e:
            return CompetitorAnalysisResult(
                overview=f"Error during analysis: {str(e)}",
                recommendations=[]
            )


if __name__ == "__main__":
    agent = CompetitorAnalysisAgent()
    print("\n=== Competitor Analysis Test ===")
    
    query = "Do proper competitive analysis for Moderna in the mRNA therapeutics market, focusing on their clinical trial pipeline, market share, and key competitors."
    result = agent.answer(query)
    
    print("\nAnalysis Result (JSON):")
    print("-" * 80)
    print(result.model_dump_json(indent=2))
    print("-" * 80)
    
   