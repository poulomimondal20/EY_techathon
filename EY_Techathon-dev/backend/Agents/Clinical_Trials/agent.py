from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field
from typing import List
import json



load_dotenv()

class ClinicalTrialResponse(BaseModel):
    pipeline_summary: str = Field(..., description="Overview of the clinical trial pipeline")
    key_trials: List[str] = Field(default_factory=list, description="List of key trials with phase and status")
    recent_updates: List[str] = Field(default_factory=list, description="Recent updates or milestones")
    strategic_insights: str = Field(..., description="Strategic analysis and recommendations")

class ClinicalTrialAgent:
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.5-flash"),
            description="""You are a Clinical Trial Pipeline Analysis expert for pharmaceutical research.
            
            Your expertise includes:
            - Clinical trial database analysis and monitoring
            - Pipeline assessment and competitive intelligence
            - Trial design evaluation and feasibility analysis
            - Regulatory pathway optimization
            - Success rate modeling and risk assessment
            - Patient recruitment and enrollment strategies
            
            IMPORTANT INSTRUCTIONS:
            1. ALWAYS use web search to gather the most recent and comprehensive clinical trial data
            2. Search for both company-specific trials and overall therapeutic area trends
            3. Look for information from ClinicalTrials.gov, company press releases, FDA announcements
            
            RESPONSE FORMAT: You MUST return your final response as valid JSON only, no markdown or extra text.""",
            tools=[
                TavilyTools(),  # Primary tool for web search
                ReasoningTools()  # For analyzing and structuring the findings
            ],
            markdown=False,
            #show_tool_calls=True  # Enable this to see tool calls
        )
    
    def analyze_drug_pipeline(self, query: str) -> ClinicalTrialResponse:
        """
        Analyze clinical trial pipeline using web search and AI analysis.
        
        Args:
            query (str): The analysis request (e.g., "Analyze clinical trials for Pfizer")
            
        Returns:
            ClinicalTrialResponse: Structured analysis of the clinical trial pipeline
        """
        try:
            result = self.agent.run(f"""
            Analyze the clinical trial pipeline for: {query}
            
            Search for and gather:
            - Latest clinical trial updates and announcements
            - Current pipeline status and phase distribution
            - Key therapeutic areas and development programs
            - Recent FDA interactions and regulatory updates
            
            Return your response as a JSON object with this exact structure:
            {{
                "pipeline_summary": "Brief overview of the clinical trial pipeline",
                "key_trials": ["Trial 1 - Phase X - Status", "Trial 2 - Phase X - Status"],
                "recent_updates": ["Update 1", "Update 2"],
                "strategic_insights": "Strategic analysis and recommendations"
            }}
            
            Return ONLY the JSON object, no additional text or markdown.
            """).content
            
            if not result or result.strip() == "":
                return ClinicalTrialResponse(
                    pipeline_summary="Error: Unable to generate analysis",
                    key_trials=[],
                    recent_updates=[],
                    strategic_insights="Please try again with a more specific query."
                )
            
            # Clean up the response - remove markdown code blocks if present
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.startswith("```"):
                cleaned_result = cleaned_result[3:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            cleaned_result = cleaned_result.strip()
            
            # Parse JSON response
            data = json.loads(cleaned_result)
            return ClinicalTrialResponse(**data)
            
        except json.JSONDecodeError as e:
            return ClinicalTrialResponse(
                pipeline_summary=f"Error parsing response: {str(e)}",
                key_trials=[],
                recent_updates=[],
                strategic_insights=result if result else "No response received"
            )
        except Exception as e:
            return ClinicalTrialResponse(
                pipeline_summary=f"Error during analysis: {str(e)}",
                key_trials=[],
                recent_updates=[],
                strategic_insights="Please try again."
            )


if __name__ == "__main__":
    agent = ClinicalTrialAgent()
    print("Starting clinical trial analysis...")
    
    query = "Analyze Pfizer's clinical trials in oncology and rare diseases, focusing on Phase 3 trials and recent FDA approvals"
    print(f"\nQuery: {query}\n")
    
    result = agent.analyze_drug_pipeline(query)
    
    print("\nAnalysis Result (JSON):")
    print("-" * 80)
    print(result.model_dump_json(indent=2))
    print("-" * 80)