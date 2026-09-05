from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv

load_dotenv()

class WebSearchAgent:    
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are an intelligent web search and research assistant with expertise in:
            
            - Comprehensive web searches across multiple sources
            - Information gathering, analysis, and synthesis
            - Fact-checking and source verification
            - Providing accurate, up-to-date information
            - Organizing complex information into clear, structured responses
            - Identifying reliable and authoritative sources
            - Summarizing key findings and insights
            
            Always provide well-researched, accurate, and comprehensive responses.
            Use multiple sources when available and clearly cite your sources.
            Present information in a clear, organized manner and highlight any limitations or uncertainties.""",
            tools=[DuckDuckGoTools(), TavilyTools()],
            markdown=True
        )
    
    def search_topic(self, topic: str) -> str:
        prompt = f"Search for comprehensive information about: {topic}. Provide detailed findings with sources."
        return self.agent.run(prompt).content  
    
    def research_question(self, question: str) -> str:
        prompt = f"Research and provide a comprehensive answer to: {question}"
        return self.agent.run(prompt).content
        

if __name__ == "__main__":
    search_agent = WebSearchAgent()
    answer = search_agent.search_topic("artificial intelligence trends 2024")
    print(answer)