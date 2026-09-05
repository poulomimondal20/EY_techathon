from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional


load_dotenv()


class QueryResponse(BaseModel):
    agent_list: list = Field(..., description="List of agents to be used for the query")
    justification: str = Field(..., description="Justification for the selected agents")


class MasterAgent:
    AVAILABLE_AGENTS = [
        "Drug Discovery Agent",
        "Medicine Validation Agent",
        "Market Insights Agent",
        "Clinical Trial Agent",
        "Deep Research Agent",
        "Patent Search Agent",
        "Web Search Agent"
    ]
    
    def __init__(self, model_id: str = "gemini-2.0-flash"):
        self.model_id = model_id
        self.agent = self._initialize_agent()
    
    def _initialize_agent(self) -> Agent:
        description = f"""
        You are the coordinator of a team of specialized agents: {', '.join(self.AVAILABLE_AGENTS)}.
        Do not answer any questions which are not related to pharmaceutical research, drug discovery, clinical trials, or medicine validation, so keep a guard against irrelevant queries.
        You will be working as a router to delegate tasks to the appropriate agents based on user queries.
        Give the list of agents that are most relevant to the query and a justification for why you chose those agents.
        """
        
        return Agent(
            model=Gemini(id=self.model_id),
            description=description,
            tools=[ReasoningTools()],
            output_schema=QueryResponse,
            markdown=True
        )
    
    def route_query(self, query: str) -> Optional[QueryResponse]:
        if not query or not query.strip():
            print("Error: Query cannot be empty")
            return None
        
        try:
            response = self.agent.run(query)
            return response.content
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return None
    
    def get_available_agents(self) -> list:
        return self.AVAILABLE_AGENTS.copy()
    
    def process_query(self, query: str, verbose: bool = True) -> Optional[dict]:
        result = self.route_query(query)
        
        if result:
            output = {
                "agent_list": result.agent_list,
                "justification": result.justification
            }
            
            if verbose:
                print("\n" + "="*50)
                print("QUERY ROUTING RESULT")
                print("="*50)
                print(f"\nQuery: {query}")
                print(f"\nSelected Agents: {', '.join(output['agent_list'])}")
                print(f"\nJustification: {output['justification']}")
                print("="*50 + "\n")
            
            return output
        
        return None


def main():

    master_agent = MasterAgent()
    
    example_queries = [
        "What are the latest developments in cancer drug discovery?",
        "How can I validate the efficacy of a new diabetes medication?",
        "What are the market trends for cardiovascular drugs?"
    ]
    
    for q in example_queries:
        print(f"\nProcessing: {q}")
        answer = master_agent.process_query(q)
        print(f"Answer: {answer}")
    

if __name__ == "__main__":
    main()