from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))

try:
    from Drug_Likliness import calculate_qed_score
    from Molecular_Design import MolecularDesigner
    from SyntheticAccessibility import SyntheticAccessibilityScorer
except ImportError as e:
    print(f"Warning: Custom tools not found: {e}")

load_dotenv()

class LeadOptimizationAgent:
    def __init__(self):
        try:
            self.molecular_designer = MolecularDesigner()
            self.sa_scorer = SyntheticAccessibilityScorer()
            tools_list = [
                DuckDuckGoTools(), 
                TavilyTools(), 
                calculate_qed_score,
                self._calculate_properties_wrapper,
            ]
        except:
            tools_list = [DuckDuckGoTools(), TavilyTools()]
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a world-class medicinal chemist serving as a Lead Optimization Agent. 
            Your primary directive is to iteratively refine lead compounds through systematic 
            Design-Predict-Analyze cycles to create superior pre-clinical candidates.
            
            Core Capabilities:
            - Structure-based drug design and optimization
            - Molecular property prediction and assessment
            - Binding affinity improvement strategies
            - Drug-likeness optimization (QED, Lipinski compliance)
            - Iterative analog generation and evaluation
            
            AVAILABLE TOOLS:
            - Literature search and target information research
            - ADMET property prediction and assessment
            - Drug-likeness and synthetic accessibility evaluation
            - Systematic analysis and hypothesis generation
            
            You must execute systematic optimization cycles with clear documentation
            of hypotheses, modifications, and outcomes for transparent decision-making.""",
            tools=tools_list,
            markdown=True
        )
    
    def _generate_analogs_wrapper(self, smiles: str, strategy: str = "diverse", num_analogs: int = 3):
        try:
            if strategy == "diverse":
                analogs = self.molecular_designer.generate_analog_series(smiles, num_analogs)
            elif strategy == "aromatic_decoration":
                analogs = []
                for decoration in ['F', 'Cl', 'CH3', 'OH', 'NH2']:
                    analog_smiles = self.molecular_designer.decorate_aromatic_ring(smiles, decoration)
                    if analog_smiles:
                        props = self.molecular_designer.get_molecular_properties(analog_smiles)
                        analogs.append({
                            'smiles': analog_smiles,
                            'strategy': 'aromatic_decoration',
                            'modification': decoration,
                            'properties': props
                        })
                    if len(analogs) >= num_analogs:
                        break
            elif strategy == "bioisosteres":
                bio_analogs = self.molecular_designer.generate_bioisosteres(smiles)
                analogs = []
                for bio_smiles in bio_analogs[:num_analogs]:
                    props = self.molecular_designer.get_molecular_properties(bio_smiles)
                    analogs.append({
                        'smiles': bio_smiles,
                        'strategy': 'bioisosteric_replacement',
                        'modification': 'bioisostere',
                        'properties': props
                    })
            else:
                analogs = self.molecular_designer.generate_analog_series(smiles, num_analogs)
            
            return {"analogs": analogs, "count": len(analogs)}
        except Exception as e:
            return {"error": f"Analog generation failed: {str(e)}", "analogs": [], "count": 0}
    
    def _calculate_properties_wrapper(self, smiles: str):
        try:
            props = self.molecular_designer.get_molecular_properties(smiles)
            
            # Add Lipinski rule compliance check
            lipinski_violations = 0
            if props.get('molecular_weight', 0) > 500:
                lipinski_violations += 1
            if props.get('logP', 0) > 5:
                lipinski_violations += 1
            if props.get('hbd', 0) > 5:
                lipinski_violations += 1
            if props.get('hba', 0) > 10:
                lipinski_violations += 1
            
            props['lipinski_violations'] = lipinski_violations
            props['drug_like'] = lipinski_violations <= 1
            
            return props
        except Exception as e:
            return {"error": f"Property calculation failed: {str(e)}"}
    
    def _calculate_sa_score_wrapper(self, smiles: str):
        """Wrapper function for synthetic accessibility scoring."""
        try:
            sa_score = self.sa_scorer.calculate_sa_score(smiles)
            return {"sa_score": round(sa_score, 2), "synthesis_feasible": sa_score <= 6.0}
        except Exception as e:
            return {"error": f"SA Score calculation failed: {str(e)}"}
    
    def _predict_toxicity_wrapper(self, smiles: str):
        """Wrapper function for toxicity prediction."""
        try:
            toxicity_report = self.tox_predictor.predict_toxicity(smiles)
            return toxicity_report if toxicity_report else {"error": "Toxicity prediction failed"}
        except Exception as e:
            return {"error": f"Toxicity prediction failed: {str(e)}"}
    
    def optimize_lead(self, target_pdb: str, lead_smiles: str, optimization_goals: dict = None) -> str:
        
        if optimization_goals is None:
            optimization_goals = {
                "primary": "Improve predicted binding affinity by at least 1 kcal/mol",
                "secondary": "Maintain or improve QED score",
                "constraint": "Do not add more than 1 Lipinski rule violation"
            }
        
        prompt = f"""
        **LEAD OPTIMIZATION MISSION**
        
        **Target Information:**
        - **Target PDB Structure:** {target_pdb}
        - **Lead Compound SMILES:** {lead_smiles}
        
        **Optimization Goals:**
        1. Primary Goal: {optimization_goals.get('primary', 'Improve binding affinity')}
        2. Secondary Goal: {optimization_goals.get('secondary', 'Maintain drug-likeness')} 
        3. Constraint: {optimization_goals.get('constraint', 'Maintain Lipinski compliance')}

        Execute the following **3-Round Iterative Optimization Workflow**:

        ## INITIAL BASELINE ASSESSMENT

        **Action 0.1 - Lead Compound Analysis:**
        First, analyze the initial lead compound using calculate_properties():
        - Get baseline molecular properties, QED score, and Lipinski violations
        - Use predict_admet_with_admet_ai() for comprehensive ADMET profiling
        - Document the starting point for optimization

        **Action 0.2 - Target Literature Research:**
        Use web search tools to research the target protein:
        - Key binding site residues and interactions
        - Known inhibitors and their binding modes
        - Structure-activity relationships (SAR) insights

        ---

        ## ROUND 1: FIRST OPTIMIZATION CYCLE

        ### Phase 1: In-Depth Analysis of Current Compound
        **Action 1.1 - Simulated Docking Analysis:**
        Based on literature and target knowledge:
        - Simulate AutoDock Vina docking (estimate binding score: -6 to -9 kcal/mol range)
        - Identify key binding interactions (H-bonds, hydrophobic contacts)
        - Document "missed opportunities" in the binding pocket

        **Action 1.2 - Interaction Profiling:**
        Create a detailed binding hypothesis:
        - Map current lead interactions to binding site residues
        - Identify unoccupied space or potential new interactions
        - Prioritize modification sites based on structure

        ### Phase 2: Rational Design of New Analogs
        **Action 2.1 - Hypothesis Generation:**
        Formulate THREE distinct modification hypotheses:
        1. **Hypothesis A**: [Specific chemical modification and rationale]
        2. **Hypothesis B**: [Alternative modification approach]
        3. **Hypothesis C**: [Third modification strategy]

        **Action 2.2 - Molecule Generation:**
        Use generate_analogs() with different strategies:
        - Strategy 1: "aromatic_decoration" for ring substitutions
        - Strategy 2: "bioisosteres" for functional group replacements  
        - Strategy 3: "diverse" for broader chemical space exploration

        ### Phase 3: Predictive Assessment
        **Action 3.1 - Property Evaluation:**
        For each generated analog, use calculate_properties() and calculate_qed_score():
        - Calculate molecular descriptors and drug-likeness
        - Estimate binding affinity improvements (simulate docking scores)
        - Check Lipinski rule compliance

        **Action 3.2 - ADMET Profiling:**
        Use predict_admet_with_admet_ai() for top analogs:
        - Assess pharmacokinetic properties
        - Identify potential liabilities
        - Compare with lead compound ADMET profile

        **Action 3.3 - Results Table:**
        | Analog | SMILES | Est. Affinity (kcal/mol) | Δ Affinity | QED Score | Lipinski Violations | Key Modification |
        |--------|--------|-------------------------|------------|-----------|-------------------|------------------|
        | Lead   | {lead_smiles} | [Baseline] | - | [Score] | [Count] | Original |
        | R1-A1  | [Generated] | [Estimated] | [Change] | [Score] | [Count] | [Modification] |
        | R1-A2  | [Generated] | [Estimated] | [Change] | [Score] | [Count] | [Modification] |
        | R1-A3  | [Generated] | [Estimated] | [Change] | [Score] | [Count] | [Modification] |

        ### Phase 4: Reflection and Selection
        **Action 4.1 - Analysis:**
        Evaluate Round 1 results using ReasoningTools():
        - Which hypotheses were successful/unsuccessful?
        - What SAR patterns emerged?
        - Any unexpected property changes?

        **Action 4.2 - Selection:**
        Select the best analog for Round 2:
        - Prioritize based on optimization goals
        - Document selection rationale
        - Update compound for next round

        ---

        ## ROUND 2: SECOND OPTIMIZATION CYCLE

        Repeat the same 4-phase process with the selected compound from Round 1:
        - Focus on further refinement based on Round 1 learnings
        - Consider combination strategies (e.g., multiple modifications)
        - Maintain optimization goal priorities

        ---

        ## ROUND 3: FINAL OPTIMIZATION CYCLE

        Execute the final optimization round:
        - Apply most promising strategies from previous rounds
        - Consider fine-tuning modifications
        - Focus on balancing all optimization criteria

        ---

        ## FINAL OUTPUT SUMMARY

        **Action: Comprehensive Final Report**

        **1. Optimized Lead Candidate:**
        - Final SMILES string
        - Complete property profile
        - ADMET assessment summary

        **2. Optimization Trajectory:**
        Present a progression table showing improvement across rounds:
        | Round | Compound | Est. Affinity | QED Score | Lipinski Violations | Key Modifications |
        |-------|----------|---------------|-----------|-------------------|-------------------|
        | 0     | Lead     | [Score]       | [Score]   | [Count]           | Starting point    |
        | 1     | Best-R1  | [Score]       | [Score]   | [Count]           | [Modifications]   |
        | 2     | Best-R2  | [Score]       | [Score]   | [Count]           | [Modifications]   |
        | 3     | Final    | [Score]       | [Score]   | [Count]           | [Modifications]   |

        **3. Final Justification:**
        - Quantify improvements achieved vs. goals
        - Explain key structure-activity relationships discovered
        - Recommend next steps for experimental validation
        - Highlight any remaining optimization opportunities

        **4. Risk Assessment:**
        - Potential liabilities in final candidate
        - Synthetic accessibility considerations
        - Intellectual property landscape review

        Begin the systematic 3-round optimization process now, using all available tools strategically.
        """
        
        return self.agent.run(prompt).content


if __name__ == "__main__":
    opt_agent = LeadOptimizationAgent()
    
    target_pdb = "1ACJ"  # Acetylcholinesterase 
    lead_compound = "CCN(CC)C(=O)c1ccc(N)cc1"  # Simple lead structure
    
    optimization_goals = {
        "primary": "Improve predicted binding affinity by at least 1.5 kcal/mol",
        "secondary": "Maintain QED score above 0.6",
        "constraint": "Maximum 1 Lipinski rule violation allowed"
    }
    
    report = opt_agent.optimize_lead(target_pdb, lead_compound, optimization_goals)
    print(report)
       