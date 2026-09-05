from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))

try:
    from Admet_properties import predict_admet_with_admet_ai
except ImportError as e:
    print(f"Warning: Custom API tools not found: {e}")

load_dotenv()

class LeadIdentificationAgent:
    def __init__(self):
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a world-class computational chemist serving as a Lead Identification Agent. 
            Your primary directive is to execute a comprehensive virtual screening workflow to identify 
            the top 5-10 promising lead compounds for a given protein target.
            
            Core Capabilities:
            - Virtual screening cascade implementation
            - Molecular property analysis and filtering
            - Structure-based drug design and docking analysis
            - ADMET property prediction and assessment
            - Lead compound optimization and ranking
            
            AVAILABLE SPECIALIZED TOOL:
            - **predict_admet_with_admet_ai(smiles_string)**: Predict comprehensive ADMET properties for compounds
            
            VIRTUAL SCREENING PROTOCOL:
            Phase 1: Library Preparation & Initial Filtering (Lipinski/Lead-like rules)
            Phase 2: Shape-Based Screening (if reference ligand available)
            Phase 3: Structure-Based Docking (AutoDock Vina simulation)
            Phase 4: Re-scoring & ADMET Filtering (AI-based scoring + ADMET prediction)
            Phase 5: Final Selection & Diversity Analysis
            
            You must systematically execute each phase, document intermediate results, 
            and provide transparent justifications for compound selection decisions.""",
            tools=[predict_admet_with_admet_ai],
            markdown=True
        )
    
    def identify_leads(self, protein_name: str, pdb_id: str, known_active_smiles: str = None) -> str:
        prompt = f"""
        **LEAD IDENTIFICATION MISSION**
        
        **Target Information:**
        - **Protein Name:** {protein_name}
        - **PDB ID for Docking:** {pdb_id}
        - **Known Active Ligand:** {known_active_smiles if known_active_smiles else "None provided"}

        Execute the following **Virtual Screening Cascade Protocol**:

        ## PHASE 1: LIBRARY PREPARATION & INITIAL FILTERING

        **Action 1.1 - Library Sourcing:**
        - Research and propose compound libraries suitable for {protein_name}
        - Estimate total number of starting compounds
        - Document library characteristics and vendor information

        **Action 1.2 - Lead-Like Property Filtering:**
        Apply the following filters to ensure "lead-like" characteristics:
        - Molecular Weight (MW): 250-450 Da
        - LogP: ≤ 4.5
        - Rotatable Bonds: ≤ 8
        - No PAINS substructures
        - **Deliverable:** Estimate compounds remaining after filtering

        ## PHASE 2: SHAPE-BASED SCREENING (Conditional)
        
        **Conditional Logic:** Execute only if known active ligand is provided.
        
        **Action 2.1 - 3D Shape Similarity:**
        - Describe shape-based screening approach using the known active as template
        - Propose selection of top 1% based on TanimotoCombo score
        - **Deliverable:** Estimated advancement numbers and strategy

        ## PHASE 3: STRUCTURE-BASED DOCKING

        **Action 3.1 - Target Analysis:**
        - Analyze the {pdb_id} structure for binding site characteristics
        - Identify key binding interactions and druggable pockets
        - Document structural considerations for docking

        **Action 3.2 - Virtual Docking Strategy:**
        - Describe AutoDock Vina docking approach for the compound library
        - Propose ranking by binding affinity (kcal/mol)
        - Select strategy for top 1,000 compounds
        - **Deliverable:** Docking methodology and selection criteria

        ## PHASE 4: RE-SCORING & ADMET FILTERING

        **Action 4.1 - High-Precision Re-Docking:**
        - Describe Schrödinger Glide SP mode simulation for top compounds
        - Propose re-ranking strategy by GlideScore
        - **Deliverable:** Scoring methodology comparison

        **Action 4.2 - AI-Based Scoring:**
        - Describe RF-Score/NN-Score analysis approach
        - Propose orthogonal validation strategy
        - **Deliverable:** AI scoring integration plan

        **Action 4.3 - ADMET Profiling:**
        For representative lead compounds, use predict_admet_with_admet_ai() to:
        - Generate comprehensive ADMET profiles for example compounds
        - Demonstrate ADMET property analysis
        - Show how to flag major liabilities (toxicity, BBB permeability, CYP inhibition)
        - **Deliverable:** ADMET analysis examples and filtering criteria

        ## PHASE 5: FINAL HIT SELECTION & REPORT

        **Action 5.1 - Scaffold Analysis:**
        - Describe compound clustering by chemical scaffold
        - Propose diversity selection strategy
        - **Deliverable:** Scaffold diversity methodology

        **Action 5.2 - Literature Integration:**
        - Describe validation approach for final candidates
        - Propose prior art and development status research
        - **Deliverable:** Literature validation strategy

        **Action 5.3 - Final Lead Compound Report:**
        Generate a template for the **TOP 5-10 LEAD CANDIDATES**:

        | Rank | Compound ID | SMILES | Vina Score | Glide Score | AI Score | Key ADMET Properties | Scaffold Group | Justification |
        |------|------------|--------|------------|-------------|----------|-------------------|----------------|---------------|
        | 1    | Example-1  | C1CC... | -8.5      | -9.2        | 7.8      | Good BBB, Low CYP  | Benzimidazole  | High affinity, clean profile |

        Provide methodology for each component:
        - **Binding Scores:** Computational affinity prediction protocols
        - **ADMET Assessment:** Key pharmacological property evaluation
        - **Risk Analysis:** Liability identification and mitigation
        - **Development Priority:** Experimental validation rationale

        **Final Recommendation:** Provide a systematic approach for lead prioritization and experimental testing strategy.

        Begin the virtual screening analysis framework now, focusing on methodology and ADMET integration.
        """
        
        return self.agent.run(prompt).content


if __name__ == "__main__":
    lead_agent = LeadIdentificationAgent()
    protein = "Acetylcholinesterase"
    pdb = "1ACJ"
    known_ligand = "CCN(CC)C(=O)c1ccc(N)cc1" 
    
    report = lead_agent.identify_leads(protein, pdb, known_ligand)
    print(report)
       