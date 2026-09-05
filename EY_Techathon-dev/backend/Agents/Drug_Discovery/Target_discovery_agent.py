from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))

try:
    from StringDBAPI import StringDBAPI
    from ChemLabAPI import ChEMBLAPI
    from UniProtAPI import UniProtAPI
    from PDBQueryTool import PDBQueryTool
except ImportError as e:
    print(f"Warning: Custom API tools not found: {e}")

load_dotenv()

class TargetDiscoveryAgent:
    def __init__(self):
        try:
            self.stringdb = StringDBAPI()
            self.chembl = ChEMBLAPI()
            self.uniprot = UniProtAPI()
            self.pdb_tool = PDBQueryTool()
            tools_list = [DuckDuckGoTools(), TavilyTools(), ReasoningTools(), 
                         self.chembl.get_target_bioactivities, self.pdb_tool.get_structure_summary, 
                         self.stringdb.get_interaction_network, self.uniprot.fetch_protein_data]
        except:
            tools_list = [DuckDuckGoTools(), TavilyTools(), ReasoningTools()]
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a world-class computational biologist serving as a Target Discovery Agent. 
            Your primary directive is to produce deeply reasoned and fully transparent reports identifying 
            the most promising therapeutic targets for diseases using Chain-of-Thought reasoning.
            
            Core Capabilities:
            - Pathophysiology analysis and hypothesis generation
            - Multi-modal evidence gathering from literature
            - Protein target evaluation and druggability assessment  
            - Risk-benefit analysis for therapeutic interventions
            - Synthesis of complex biological data into actionable insights
            
            AVAILABLE TOOLS:
            1. **DuckDuckGoTools & TavilyTools**: For literature search and general research
            2. **ReasoningTools**: For systematic thinking and evidence evaluation
            
            You must externalize your reasoning at every step and provide transparent justifications
            for all conclusions. Focus on literature-based analysis and systematic evaluation.""",
            tools=tools_list,
            markdown=True
        )
    
    def discover_target(self, disease_name: str) -> str:
        prompt = f"""
        **TARGET DISCOVERY MISSION FOR: {disease_name}**
        
        Execute a comprehensive literature-based target discovery analysis:
        
        ## STEP 1: DISEASE PATHOPHYSIOLOGY RESEARCH
        Use DuckDuckGoTools to research {disease_name} and identify:
        - Key pathological mechanisms and pathways
        - Current understanding of disease progression
        - Existing therapeutic approaches and their limitations
        - Molecular targets already under investigation
        
        ## STEP 2: HYPOTHESIS GENERATION
        Based on the research, formulate THREE distinct therapeutic hypotheses:
        - **Hypothesis A**: [Pathway restoration approach] - Focus on restoring disrupted cellular pathways
        - **Hypothesis B**: [Protein inhibition approach] - Focus on inhibiting disease-driving proteins  
        - **Hypothesis C**: [Protein-protein interaction disruption] - Focus on breaking pathological interactions
        
        For each hypothesis, clearly state:
        - The biological rationale
        - The therapeutic mechanism  
        - Specific target candidates
        
        ## STEP 3: EVIDENCE EVALUATION
        Use ReasoningTools to systematically evaluate each hypothesis:
        - Literature support strength
        - Clinical evidence availability
        - Druggability considerations
        - Safety profile assessment
        
        ## STEP 4: TARGET PRIORITIZATION
        Rank the target candidates based on:
        - Scientific evidence strength
        - Druggability potential
        - Competitive landscape
        - Development feasibility
        
        ## STEP 5: FINAL RECOMMENDATION
        Provide an executive summary with:
        - Top 2-3 prioritized targets
        - Evidence-based rationale for selection
        - Risk assessment for each target
        - Recommended next steps for validation
        
        Begin the systematic analysis now, using literature search strategically.
        """
        
        return self.agent.run(prompt).content


if __name__ == "__main__":
    target_agent = TargetDiscoveryAgent()
    disease = "Alzheimer's disease"
    report = target_agent.discover_target(disease)
    print(report)
        
        