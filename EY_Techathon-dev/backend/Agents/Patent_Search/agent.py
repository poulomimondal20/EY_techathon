import os
import sys
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))

try:
    from patent_search_tool import PatentSearchTool
except ImportError as e:
    print(f"Warning: Patent search tool not found: {e}")

load_dotenv()

class PatentSearchAgent:
    def __init__(self):
        self.patent_tool = PatentSearchTool()
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"), 
            description="""You are a world-class patent search and analysis agent specializing in pharmaceutical patents. 
            Your primary directive is to conduct comprehensive patent searches and provide detailed analyses of 
            intellectual property landscapes, patent validity, and competitive intelligence.
            
            Core Capabilities:
            - Patent search by keyword, drug name, inventor, or assignee
            - Patent landscape analysis and competitive intelligence
            - Patent validity and prior art analysis
            - IP freedom to operate assessments
            - Patent portfolio evaluation
            
            Available Tools:
            1. **TavilyTools**: Web search for patent-related information
            2. **search_drug_patents(disease_name)**: Search pharmaceutical patents by disease
            3. **search_by_keyword(keyword)**: General patent keyword search
            4. **search_specific_patent(patent_id)**: Get detailed info for specific patent
            
            If tool calls fail, do not halt execution. Instead, provide analysis based on available information.
            Dont mention tool call failures in the final response.
            Always provide comprehensive analysis with patent numbers, titles, key claims,
            and strategic recommendations for IP development or licensing.""",
            tools=[
                TavilyTools(),
                self._search_drug_patents_wrapper,
                self._search_by_keyword_wrapper, 
                self._search_specific_patent_wrapper
            ],
            markdown=True
        )
    
    def _search_drug_patents_wrapper(self, disease_name: str):
        try:
            results = self.patent_tool.search_by_keyword(f"{disease_name} drug treatment pharmaceutical")
            return {"results": results, "count": len(results)}
        except Exception as e:
            return {"error": f"Disease patent search failed: {str(e)}"}
    
    def _search_by_keyword_wrapper(self, keyword: str):
        try:
            results = self.patent_tool.search_by_keyword(keyword)
            return {"results": results, "count": len(results)}
        except Exception as e:
            return {"error": f"Keyword search failed: {str(e)}"}
    
    def _search_specific_patent_wrapper(self, patent_id: str):
        try:
            results = self.patent_tool.search_specific_patent(patent_id)
            return {"results": results, "count": len(results)}
        except Exception as e:
            return {"error": f"Specific patent search failed: {str(e)}"}
    
    def search_patents(self, query: str) -> str:
        return self.agent.run(query).content
    
    def analyze_patent_landscape(self, technology_area: str) -> str:
        landscape_query = f"""
        Conduct a comprehensive patent landscape analysis for: {technology_area}
        
        Please perform the following analysis:
        
        1. **Technology Overview**: Use web search to understand the current state of {technology_area}
        
        2. **Patent Search Strategy**: 
           - Use search_by_keyword() to find relevant patents
           - Search for key terms related to {technology_area}
           - Identify major patent families and applications
        
        3. **Key Player Analysis**:
           - Identify top patent holders and inventors
           - Analyze patent filing trends over time
           - Map competitive landscape
        
        4. **Patent Quality Assessment**:
           - Evaluate key patents for strength and validity
           - Identify potential prior art issues
           - Assess claim scope and enforceability
        
        5. **Strategic Recommendations**:
           - Identify white space opportunities
           - Recommend patent filing strategies
           - Assess freedom to operate risks
           - Suggest potential licensing opportunities
        
        Provide detailed analysis with specific patent examples, filing statistics, and actionable insights.
        """
        
        return self.agent.run(landscape_query).content
    
    def validate_patent(self, patent_id: str) -> str:
        validation_query = f"""
        Perform comprehensive patent validity analysis for patent: {patent_id}
        
        Analysis Framework:
        
        1. **Patent Details**: Use search_specific_patent() to get full patent information
        
        2. **Prior Art Search**: 
           - Search for relevant prior art using keyword searches
           - Identify potential invalidating references
           - Analyze publication dates and priority claims
        
        3. **Claim Analysis**:
           - Evaluate claim scope and limitations
           - Assess claim construction issues
           - Identify potential indefiniteness or enablement problems
        
        4. **Validity Assessment**:
           - Novelty analysis against prior art
           - Non-obviousness evaluation
           - Written description and enablement review
        
        5. **Strategic Implications**:
           - Likelihood of successful validity challenge
           - Potential invalidity arguments
           - Recommendations for litigation or licensing
        
        Do not mention tool call failures in the final response.
        Provide detailed analysis with specific prior art references and validity conclusions.
        """
        
        return self.agent.run(validation_query).content


if __name__ == "__main__":
    patent_agent = PatentSearchAgent()
    
    print("=== Patent Search Agent Test ===")
    
    # Comprehensive patent analysis prompt
    patent_query = """
    Conduct comprehensive patent landscape analysis for Alzheimer's disease treatments with focus on:
    
    1. **Patent Search Strategy**:
       - Use search_by_keyword() to find patents for "Alzheimer drug treatment"
       - Search for "tau protein inhibitor patents"
       - Look for "amyloid beta therapeutic patents"
    
    2. **Competitive Intelligence**:
       - Identify major pharmaceutical companies with Alzheimer's patents
       - Analyze patent filing trends over the last 5 years
       - Map key inventors and research institutions
    
    3. **Technology Assessment**:
       - Categorize patents by mechanism of action (tau, amyloid, inflammation)
       - Assess patent strength and claim scope
       - Identify potential white space opportunities
    
    4. **Strategic Analysis**:
       - Evaluate freedom to operate risks for new drug development
       - Identify potential licensing opportunities
       - Recommend patent filing strategies
       - Assess litigation risks and patent landscapes
    
    5. **Market Impact**:
       - Analyze patent expiry dates and generic entry timelines
       - Evaluate impact on drug pricing and market competition
       - Identify upcoming patent cliffs and opportunities
    
    Provide specific patent examples with numbers, key claims analysis, and strategic recommendations.
    """
    
    patent_result = patent_agent.search_patents(patent_query)
    print(patent_result)
    
    print("\n" + "="*80)

