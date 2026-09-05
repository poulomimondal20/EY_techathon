from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from agno.tools.tavily import TavilyTools
from agno.tools.baidusearch import BaiduSearchTools 
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
import sys


load_dotenv()

class MarketInsightsResponse(BaseModel):
    market_overview: str = Field(..., description="Overview of the pharmaceutical market")
    market_size: Optional[str] = Field(None, description="Current market size and growth projections")
    key_players: List[str] = Field(default_factory=list, description="Major companies and their market positions")
    pricing_analysis: str = Field(..., description="Pricing trends and recommendations")
    competitive_landscape: List[str] = Field(default_factory=list, description="Competitive insights and market dynamics")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Actionable strategic recommendations")

class MarketInsightsAgent:
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a pharmaceutical market intelligence expert specializing in 
            market analysis, pricing strategies, and competitive landscapes.
            
            IMPORTANT: You MUST use the web search tools (Tavily or Baidu) to find real, current market data.
            DO NOT make up numbers - search for actual statistics and cite sources.
            
            Core Capabilities:
            - Drug market price prediction and analysis with REAL market data
            - Competitive landscape assessment with actual company financials
            - Market sizing with verified industry reports (search for them!)
            - Strategic market positioning recommendations based on current trends
            
            ALWAYS search the web first before answering. Use multiple searches if needed.
            
            RESPONSE FORMAT: Return your final response as valid JSON only, no markdown or extra text.""",
            tools=[
                ReasoningTools(),
                TavilyTools(),
                BaiduSearchTools(),
            ],
            markdown=False
        )

    
    def analyze_market(self, query: str) -> MarketInsightsResponse:
        try:
            result = self.agent.run(f"""
            Analyze the pharmaceutical market for: {query}
            
            IMPORTANT INSTRUCTIONS:
            1. You MUST use the Tavily web search tool to find REAL, CURRENT market data
            2. Search for: "{query} market size 2024 2025" and "{query} market share companies"
            3. DO NOT make up numbers - only use data you find from web searches
            4. Include specific dollar amounts, percentages, and growth rates from your searches
            
            Search for and gather (USE WEB SEARCH FOR EACH):
            - Market size in USD (billions), growth rate (CAGR %), and projections to 2030
            - Key players with their ACTUAL market shares and revenue figures
            - Current drug pricing (average annual cost, regional variations)
            - Recent competitive developments, M&A activity, pipeline updates
            
            After searching, return your response as a JSON object with this exact structure:
            {{
                "market_overview": "Brief overview with specific numbers from your search",
                "market_size": "Include specific figures: $XX billion in 2024, projected $XX billion by 2030, X.X% CAGR",
                "key_players": ["Company 1 - XX% market share, $X.XB revenue", "Company 2 - XX% market share"],
                "pricing_analysis": "Average treatment costs with specific numbers",
                "competitive_landscape": ["Specific insight with numbers", "Another data-backed insight"],
                "strategic_recommendations": ["Data-driven recommendation 1", "Recommendation 2"]
            }}
            
            Return ONLY the JSON object, no additional text or markdown.
            """).content
            
            if not result or result.strip() == "":
                return MarketInsightsResponse(
                    market_overview="Error: Unable to generate analysis",
                    pricing_analysis="Please try again with a more specific query.",
                    strategic_recommendations=[]
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
            return MarketInsightsResponse(**data)
            
        except json.JSONDecodeError as e:
            return MarketInsightsResponse(
                market_overview=f"Error parsing response: {str(e)}",
                pricing_analysis=result if result else "No response received",
                strategic_recommendations=[]
            )
        except Exception as e:
            return MarketInsightsResponse(
                market_overview=f"Error during analysis: {str(e)}",
                pricing_analysis="Please try again.",
                strategic_recommendations=[]
            )


if __name__ == "__main__":
    market_agent = MarketInsightsAgent()
    
    query = "Analyze the diabetes drug market including GLP-1 agonists and SGLT2 inhibitors"
    
    response = market_agent.analyze_market(query)
    print("\nMarket Analysis Result (JSON):")
    print("-" * 80)
    print(response.model_dump_json(indent=2))
    print("-" * 80)