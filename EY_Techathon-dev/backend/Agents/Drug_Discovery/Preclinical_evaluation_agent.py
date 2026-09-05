from agno.agent import Agent
from agno.models.groq import Groq
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'Tools'))

try:
    from Admet_properties import predict_admet_with_admet_ai
    from Drug_Likliness import calculate_qed_score
    from SyntheticAccessibility import SyntheticAccessibilityScorer
except ImportError as e:
    print(f"Warning: Custom tools not found: {e}")

load_dotenv()

class PreclinicalEvaluationAgent:
    def __init__(self):
        try:
            self.sa_scorer = SyntheticAccessibilityScorer()
            tools_list = [
                DuckDuckGoTools(), 
                ReasoningTools(),
                predict_admet_with_admet_ai,
                calculate_qed_score,
                self._calculate_sa_score_wrapper,
            ]
        except:
            tools_list = [DuckDuckGoTools(), ReasoningTools()]
        
        self.agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are a world-class pharmaceutical scientist serving as a Preclinical Evaluation Agent. 
            Your primary directive is to conduct comprehensive computational safety and feasibility analysis 
            on lead drug candidates to determine their suitability for clinical development.
            
            Core Capabilities:
            - In silico toxicology assessment and safety profiling
            - Drug-drug interaction risk evaluation
            - Synthetic accessibility and feasibility analysis
            - Risk-benefit analysis and go/no-go decisions
            - Regulatory compliance assessment
            
            You must provide transparent, evidence-based recommendations with clear
            risk categorization and actionable next steps for development teams.""",
            tools=tools_list,
            markdown=True
        )
    
    def _calculate_sa_score_wrapper(self, smiles: str):
        """Wrapper function for synthetic accessibility scoring."""
        try:
            sa_score = self.sa_scorer.calculate_sa_score(smiles)
            
            # Interpret SA score
            if sa_score <= 2.5:
                difficulty = "Very Easy"
                risk_level = "Low"
            elif sa_score <= 4.0:
                difficulty = "Easy"
                risk_level = "Low"
            elif sa_score <= 6.0:
                difficulty = "Moderate"
                risk_level = "Medium"
            elif sa_score <= 8.0:
                difficulty = "Difficult"
                risk_level = "High"
            else:
                difficulty = "Very Difficult"
                risk_level = "High"
            
            return {
                "sa_score": round(sa_score, 2),
                "difficulty": difficulty,
                "risk_level": risk_level,
                "synthesis_feasible": sa_score <= 6.0
            }
        except Exception as e:
            return {"error": f"SA Score calculation failed: {str(e)}"}
    
    def _predict_toxicity_wrapper(self, smiles: str):
        """Wrapper function for toxicity prediction."""
        try:
            toxicity_report = self.tox_predictor.predict_toxicity(smiles)
            if toxicity_report:
                return toxicity_report
            else:
                return {"error": "Toxicity prediction failed"}
        except Exception as e:
            return {"error": f"Toxicity prediction failed: {str(e)}"}
    
    def evaluate_candidate(self, compound_id: str, smiles_string: str) -> str:
        
        prompt = f"""
        **PRECLINICAL EVALUATION MISSION**
        
        **Candidate for Review:**
        - **Compound ID:** {compound_id}
        - **SMILES String:** {smiles_string}

        Execute the following **Mandatory Assessment Protocol**:

        ## PART 1: IN SILICO TOXICOLOGY PANEL

        ### Action 1.1 - General & Oral Toxicity Assessment
        **Task:** Use predict_toxicity() to evaluate general toxicity profile:
        - Predict LD50 toxicity class and structural alerts
        - Assess hepatotoxicity and general safety concerns
        - Identify any known toxic functional groups or motifs
        - **Deliverable:** Comprehensive toxicity risk assessment

        ### Action 1.2 - Cardiotoxicity Evaluation
        **Task:** Use predict_admet_with_admet_ai() to assess cardiac safety:
        - Focus on hERG channel inhibition predictions
        - Evaluate cardiotoxicity risk markers
        - Assess QT prolongation potential
        - **Deliverable:** Cardiac safety risk profile and probability scores

        ### Action 1.3 - Drug-Drug Interaction (DDI) Risk Assessment
        **Task:** Use predict_admet_with_admet_ai() for CYP450 interaction analysis:
        - Evaluate inhibition potential for major CYP isoforms (1A2, 2C9, 2C19, 2D6, 3A4)
        - Assess substrate potential and metabolic stability
        - Flag any isoform with >70% predicted inhibition risk
        - **Deliverable:** Complete DDI risk matrix with probability scores

        ## PART 2: SYNTHETIC FEASIBILITY ASSESSMENT

        ### Action 2.1 - Heuristic Synthetic Accessibility
        **Task:** Use calculate_sa_score() to evaluate synthesis difficulty:
        - Calculate SA Score (1-10 scale, lower is better)
        - Interpret score in context of drug development timelines
        - Assess commercial viability of synthesis
        - **Deliverable:** SA Score with risk categorization

        ### Action 2.2 - Retrosynthesis Planning Analysis
        **Task:** Analyze synthetic route complexity:
        - Research literature for similar structural scaffolds
        - Estimate synthetic steps and starting material availability  
        - Identify potential synthetic challenges or bottlenecks
        - Assess scalability for manufacturing
        - **Deliverable:** Synthesis feasibility assessment and step estimation

        ### Action 2.3 - Regulatory and IP Landscape
        **Task:** Use web search tools to evaluate:
        - Prior art and patent landscape around similar structures
        - Regulatory precedents for this structural class
        - Manufacturing and quality control considerations
        - **Deliverable:** Regulatory feasibility and IP risk assessment

        ## PART 3: FINAL JUDGEMENT AND RECOMMENDATION

        ### Action 3.1 - Risk Synthesis and Matrix Creation
        **Task:** Consolidate all findings into a structured "Preclinical Risk Matrix":

        Apply the following **Risk Thresholds**:
        - **Toxicity Class 1-2 or High Toxicity Probability**: High Risk
        - **hERG Risk > 50%**: High Cardiac Risk  
        - **Major CYP Inhibition > 70%**: High DDI Risk
        - **SA Score > 6.0**: High Synthesis Risk
        - **Multiple Lipinski Violations**: High Drug-likeness Risk

        **Deliverable:** Create this risk assessment table:

        | Risk Category | Finding | Risk Level | Threshold Met | Mitigation Strategy |
        |---------------|---------|------------|---------------|-------------------|
        | General Toxicity | [Result] | [Low/Med/High] | [Yes/No] | [Strategy] |
        | Cardiotoxicity | [hERG %] | [Low/Med/High] | [Yes/No] | [Strategy] |
        | Drug Interactions | [CYP Profile] | [Low/Med/High] | [Yes/No] | [Strategy] |
        | Synthetic Access | [SA Score] | [Low/Med/High] | [Yes/No] | [Strategy] |
        | Drug-likeness | [QED/Lipinski] | [Low/Med/High] | [Yes/No] | [Strategy] |

        ### Action 3.2 - Final Verdict and Recommendation
        **Task:** Based on the risk matrix, issue one of three final verdicts with detailed justification:

        **Option 1: `🟢 GO FOR DEVELOPMENT`**
        - Criteria: No high-risk categories, manageable medium risks
        - The candidate displays a clean safety profile and is synthetically feasible
        - Recommend immediate progression to in vitro studies

        **Option 2: `🟡 GO, BUT WITH FLAGS`** 
        - Criteria: 1-2 medium/high risks that are manageable
        - The candidate is promising but carries specific risks requiring attention
        - Recommend conditional progression with risk mitigation strategies

        **Option 3: `🔴 NO-GO - REJECT`**
        - Criteria: Multiple high risks or one fatal flaw
        - The candidate has unacceptable risk profile for development
        - Recommend rejection and provide specific redesign strategy

        **Deliverable Requirements:**
        1. **Clear Verdict Statement** with emoji indicator
        2. **One-paragraph Justification** explaining the decision rationale
        3. **Specific Next Steps** for the development team
        4. **Risk Mitigation Strategies** for flagged issues (if GO/conditional GO)
        5. **Redesign Recommendations** for Lead Optimization Agent (if NO-GO)

        ### Action 3.3 - Development Timeline and Resource Estimation
        **Task:** If GO decision, provide:
        - Estimated timeline to IND filing
        - Key milestone deliverables
        - Resource requirements and potential bottlenecks
        - Regulatory strategy recommendations

        **Final Output Format:**
        ```
        ## PRECLINICAL EVALUATION REPORT
        **Compound:** {compound_id}
        **SMILES:** {smiles_string}
        
        ### RISK MATRIX
        [Detailed risk table]
        
        ### FINAL VERDICT
        [Verdict with full justification]
        
        ### RECOMMENDATIONS
        [Specific actionable next steps]
        ```

        Begin the comprehensive preclinical evaluation now, using all tools systematically to build a complete risk profile.
        """
        
        return self.agent.run(prompt).content


if __name__ == "__main__":
    eval_agent = PreclinicalEvaluationAgent()
    
    # Example evaluation
    compound_id = "LEAD-OPT-001"
    candidate_smiles = "CC(C)Cc1ccc(C(C)C(=O)O)cc1"  
    
    evaluation_report = eval_agent.evaluate_candidate(compound_id, candidate_smiles)
    print(evaluation_report)
    eval_agent = PreclinicalEvaluationAgent()
    
    # Example evaluation
    compound_id = "LEAD-OPT-001"
    candidate_smiles = "CC(C)Cc1ccc(C(C)C(=O)O)cc1"  
    
    evaluation_report = eval_agent.evaluate_candidate(compound_id, candidate_smiles)
    print(evaluation_report)
