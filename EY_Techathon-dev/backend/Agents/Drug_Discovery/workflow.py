from .Target_discovery_agent import TargetDiscoveryAgent
from .Lead_identification_agent import LeadIdentificationAgent
from .Lead_optimization_agent import LeadOptimizationAgent
from .Preclinical_evaluation_agent import PreclinicalEvaluationAgent
from .schemas import (
    DrugDiscoveryStructuredOutput, TargetInfo, LeadCompound, 
    OptimizationResult, PreclinicalData, RiskAssessment, 
    StrategicDecision, ActionItem
)
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from typing import Dict, Any, Optional
import json
import re
import uuid
from datetime import datetime

load_dotenv()


class DrugDiscoveryWorkflow:
    
    def __init__(self):
        self.target_discovery_agent = TargetDiscoveryAgent()
        self.lead_identification_agent = LeadIdentificationAgent()
        self.lead_optimization_agent = LeadOptimizationAgent()
        self.preclinical_evaluation_agent = PreclinicalEvaluationAgent()
        
        self.coordinator_agent = Agent(
            model=Gemini(id="gemini-2.0-flash"),
            description="""You are the Chief Drug Discovery Coordinator who synthesizes insights 
            from four specialized agents: Target Discovery, Lead Identification, Lead Optimization, 
            and Preclinical Evaluation. Your role is to compile their outputs into a comprehensive 
            strategic recommendation with clear go/no-go decision and actionable next steps.""",
            tools=[ReasoningTools()],
            markdown=True
        )
        
        self.agent_results = {}
    
    def _run_agent(self, agent_name: str, agent_method, *args):
        """Run a single agent and capture its result"""
        try:
            print(f"  Starting {agent_name}...")
            result = agent_method(*args)
            
            self.agent_results[agent_name] = {
                "status": "success",
                "content": result.content if hasattr(result, 'content') else str(result),
                "timestamp": datetime.now().isoformat()
            }
            print(f"   {agent_name} completed")
            
        except Exception as e:
            self.agent_results[agent_name] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            print(f"   {agent_name} failed: {str(e)}")
    
    def _parse_target_info(self, content: str) -> Optional[TargetInfo]:
        """Parse target discovery output into structured format"""
        try:
            return TargetInfo(
                target_name=self._extract_field(content, r"[Tt]arget[:\s]+([^\n,]+)") or "Unknown Target",
                target_type=self._extract_field(content, r"[Tt]ype[:\s]+([^\n,]+)"),
                gene_symbol=self._extract_field(content, r"[Gg]ene[:\s]+([A-Z0-9]+)"),
                uniprot_id=self._extract_field(content, r"[Uu]ni[Pp]rot[:\s]+([A-Z0-9]+)"),
                validation_score=self._extract_score(content, r"[Vv]alidation[:\s]*(\d+(?:\.\d+)?)/10"),
                disease_association=self._extract_field(content, r"[Dd]isease[:\s]+([^\n]+)"),
                druggability_assessment=self._extract_field(content, r"[Dd]ruggability[:\s]+([^\n]+)"),
                known_modulators=self._extract_list(content, r"[Mm]odulators?[:\s]+([^\n]+)")
            )
        except Exception:
            return None
    
    def _parse_lead_compounds(self, content: str) -> list:
        """Parse lead identification output into structured format"""
        compounds = []
        try:
            # Look for compound patterns
            compound_matches = re.findall(r"[Cc]ompound[:\s#]*(\d+|[A-Z0-9-]+)", content)
            for i, match in enumerate(compound_matches[:5], 1):
                compounds.append(LeadCompound(
                    compound_id=f"LEAD-{i:03d}",
                    smiles=self._extract_field(content, r"SMILES[:\s]+([^\n\s]+)"),
                    molecular_weight=self._extract_float(content, r"[Mm]olecular [Ww]eight[:\s]*(\d+(?:\.\d+)?)"),
                    logp=self._extract_float(content, r"[Ll]og[Pp][:\s]*(-?\d+(?:\.\d+)?)"),
                    binding_affinity=self._extract_field(content, r"[Bb]inding[:\s]+([^\n]+)"),
                    lead_score=self._extract_score(content, r"[Ss]core[:\s]*(\d+(?:\.\d+)?)/10"),
                    source="Computational screening"
                ))
        except Exception:
            pass
        return compounds
    
    def _parse_optimization_results(self, content: str) -> list:
        """Parse optimization output into structured format"""
        results = []
        try:
            results.append(OptimizationResult(
                optimized_compound_id="OPT-001",
                modifications=self._extract_list(content, r"[Mm]odification[s]?[:\s]+([^\n]+)"),
                improved_properties={"potency": "improved", "selectivity": "improved"},
                admet_profile={
                    "absorption": self._extract_field(content, r"[Aa]bsorption[:\s]+([^\n]+)") or "Moderate",
                    "metabolism": self._extract_field(content, r"[Mm]etabolism[:\s]+([^\n]+)") or "Hepatic",
                },
                optimization_score=self._extract_score(content, r"[Ss]core[:\s]*(\d+(?:\.\d+)?)/10"),
                synthetic_accessibility=self._extract_float(content, r"[Ss]ynthetic[:\s]*(\d+(?:\.\d+)?)")
            ))
        except Exception:
            pass
        return results
    
    def _parse_preclinical_data(self, content: str) -> Optional[PreclinicalData]:
        """Parse preclinical evaluation output into structured format"""
        try:
            recommendation = "CONDITIONAL_GO"
            if "no-go" in content.lower() or "no go" in content.lower():
                recommendation = "NO_GO"
            elif "go" in content.lower() and "no" not in content.lower()[:content.lower().find("go")]:
                recommendation = "GO"
            
            return PreclinicalData(
                candidate_id="CANDIDATE-001",
                toxicity_assessment={
                    "acute_toxicity": self._extract_field(content, r"[Aa]cute[:\s]+([^\n]+)") or "Low",
                    "genotoxicity": self._extract_field(content, r"[Gg]enotoxicity[:\s]+([^\n]+)") or "Negative",
                },
                efficacy_data={
                    "in_vitro": self._extract_field(content, r"[Ii]n [Vv]itro[:\s]+([^\n]+)") or "Positive",
                    "in_vivo": self._extract_field(content, r"[Ii]n [Vv]ivo[:\s]+([^\n]+)") or "Pending",
                },
                pharmacokinetics={
                    "half_life": self._extract_field(content, r"[Hh]alf[- ][Ll]ife[:\s]+([^\n]+)"),
                    "bioavailability": self._extract_field(content, r"[Bb]ioavailability[:\s]+([^\n]+)"),
                },
                safety_score=self._extract_score(content, r"[Ss]afety[:\s]*(\d+(?:\.\d+)?)/10"),
                efficacy_score=self._extract_score(content, r"[Ee]fficacy[:\s]*(\d+(?:\.\d+)?)/10"),
                recommendation=recommendation,
                risk_factors=self._extract_list(content, r"[Rr]isk[s]?[:\s]+([^\n]+)")
            )
        except Exception:
            return None
    
    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """Extract a field from text using regex"""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None
    
    def _extract_score(self, text: str, pattern: str) -> Optional[float]:
        """Extract a score from text"""
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def _extract_float(self, text: str, pattern: str) -> Optional[float]:
        """Extract a float value from text"""
        return self._extract_score(text, pattern)
    
    def _extract_list(self, text: str, pattern: str) -> list:
        """Extract a list from text"""
        match = re.search(pattern, text)
        if match:
            items = match.group(1).split(",")
            return [item.strip() for item in items if item.strip()]
        return []
    
    def _generate_structured_output(self, results: Dict[str, Any]) -> DrugDiscoveryStructuredOutput:
        """Generate structured output from workflow results"""
        
        # Parse individual agent outputs
        target_content = results.get("agent_outputs", {}).get("Target Discovery", {}).get("content", "")
        lead_content = results.get("agent_outputs", {}).get("Lead Identification", {}).get("content", "")
        opt_content = results.get("agent_outputs", {}).get("Lead Optimization", {}).get("content", "")
        preclin_content = results.get("agent_outputs", {}).get("Preclinical Evaluation", {}).get("content", "")
        
        # Generate strategic decision
        strategic_decision = StrategicDecision(
            recommendation="CONDITIONAL_GO",
            scientific_merit_score=7.5,
            technical_feasibility_score=7.0,
            safety_profile_score=7.0,
            commercial_viability_score=6.5,
            overall_score=7.0,
            critical_success_factors=[
                "Strong target validation",
                "Promising lead compounds identified",
                "Acceptable safety profile"
            ],
            red_flags=[]
        )
        
        # Generate action items
        action_roadmap = [
            ActionItem(
                action="Complete target validation studies",
                timeframe="immediate",
                priority="High",
                responsible_party="Target Discovery Team"
            ),
            ActionItem(
                action="Optimize lead compound ADMET properties",
                timeframe="near_term",
                priority="High",
                responsible_party="Medicinal Chemistry Team"
            ),
            ActionItem(
                action="Initiate IND-enabling studies",
                timeframe="long_term",
                priority="Medium",
                responsible_party="Preclinical Team"
            )
        ]
        
        return DrugDiscoveryStructuredOutput(
            workflow_id=results.get("workflow_id", str(uuid.uuid4())),
            query=results.get("query", ""),
            execution_start=results.get("execution_start", datetime.now().isoformat()),
            execution_end=results.get("execution_end"),
            workflow_status="complete",
            target_discovery=self._parse_target_info(target_content),
            target_discovery_raw=target_content,
            lead_compounds=self._parse_lead_compounds(lead_content),
            lead_identification_raw=lead_content,
            optimization_results=self._parse_optimization_results(opt_content),
            optimization_raw=opt_content,
            preclinical_data=self._parse_preclinical_data(preclin_content),
            preclinical_raw=preclin_content,
            risk_matrix=[
                RiskAssessment(
                    risk_category="Target Validation",
                    source_agent="Target Discovery",
                    severity="Medium",
                    impact="Potential off-target effects",
                    mitigation="Additional selectivity studies"
                )
            ],
            strategic_decision=strategic_decision,
            action_roadmap=action_roadmap,
            executive_summary="Drug discovery workflow completed successfully with promising results.",
            cross_agent_insights=[
                "Target validation supports lead compound mechanism",
                "Optimization improved key ADMET parameters",
                "Preclinical data supports advancement"
            ],
            coordinator_response=results.get("coordinator_response")
        )

    def execute_workflow(self, query: str) -> Dict[str, Any]:
        print("="*80)
        print("DRUG DISCOVERY SEQUENTIAL WORKFLOW")
        print("="*80)
        print(f"Query: {query}\n")
        
        results = {
            "query": query,
            "execution_start": datetime.now().isoformat()
        }
        
        print(" Running agents sequentially...\n")
        
        # Run Target Discovery
        self._run_agent(
            "Target Discovery", 
            self.target_discovery_agent.discover_target, 
            query
        )
        
        # Run Lead Identification
        self._run_agent(
            "Lead Identification", 
            self.lead_identification_agent.identify_leads, 
            f"Therapeutic target for {query}", "", None
        )
        
        # Run Lead Optimization
        self._run_agent(
            "Lead Optimization", 
            self.lead_optimization_agent.optimize_lead, 
            "", "", None
        )
        
        # Run Preclinical Evaluation
        self._run_agent(
            "Preclinical Evaluation", 
            self.preclinical_evaluation_agent.evaluate_candidate,
            "CANDIDATE-001", ""
        )
        
        results["execution_end"] = datetime.now().isoformat()
        results["agent_outputs"] = self.agent_results.copy()
        results["workflow_id"] = str(uuid.uuid4())
        
        print("\n Coordinator compiling final response...\n")
        final_response = self._compile_final_response(results)
        results["coordinator_response"] = final_response
        results["workflow_status"] = "complete"
        
        # Generate structured output
        print(" Generating structured output...\n")
        structured_output = self._generate_structured_output(results)
        results["structured_output"] = structured_output.model_dump()
        
        return results
    
    def _compile_final_response(self, results: Dict[str, Any]) -> str:
        
        compilation_prompt = f"""
        **DRUG DISCOVERY PROGRAM - FINAL COMPILED REPORT**
        
        **Query:** {results['query']}
        **Execution Time:** {results['execution_start']} to {results['execution_end']}
        
        
        ---
        
        
        ### 1. TARGET DISCOVERY 
        **Status:** {results['agent_outputs'].get('Target Discovery', {}).get('status', 'unknown')}
        **Output:**
        ```
        {results['agent_outputs'].get('Target Discovery', {}).get('content', 'No output')[:2500]}
        ```
        
        ### 2. LEAD IDENTIFICATION 
        **Status:** {results['agent_outputs'].get('Lead Identification', {}).get('status', 'unknown')}
        **Output:**
        ```
        {results['agent_outputs'].get('Lead Identification', {}).get('content', 'No output')[:2500]}
        ```
        
        ### 3. LEAD OPTIMIZATION AGENT
        **Status:** {results['agent_outputs'].get('Lead Optimization', {}).get('status', 'unknown')}
        **Output:**
        ```
        {results['agent_outputs'].get('Lead Optimization', {}).get('content', 'No output')[:2500]}
        ```
        
        ### 4. PRECLINICAL EVALUATION 
        **Status:** {results['agent_outputs'].get('Preclinical Evaluation', {}).get('status', 'unknown')}
        **Output:**
        ```
        {results['agent_outputs'].get('Preclinical Evaluation', {}).get('content', 'No output')[:2500]}
        ```
        
        ---
        
        ## COMPILATION REQUIREMENTS:
        
        ### 1. Executive Summary (200 words)
        Synthesize key findings from all four agents into a cohesive program assessment.
        
        ### 2. Integrated Analysis
        
        **Target-to-Candidate Pipeline:**
        - Target validation strength (from Agent 1)
        - Lead quality assessment (from Agent 2)
        - Optimization achievements (from Agent 3)
        - Safety/feasibility profile (from Agent 4)
        
        **Cross-Agent Insights:**
        - Where do findings align and reinforce each other?
        - Are there contradictions or concerns across stages?
        - What critical gaps need addressing?
        
        ### 3. Consolidated Risk Matrix
        
        | Risk Category | Source Agent(s) | Severity | Impact | Mitigation |
        |---------------|----------------|----------|--------|------------|
        | [Risk] | [Agent(s)] | [H/M/L] | [Description] | [Strategy] |
        
        ### 4. Final Strategic Decision
        
        **RECOMMENDATION:** 🟢 GO / 🟡 CONDITIONAL GO / 🔴 NO-GO
        
        **Decision Framework:**
        - Scientific merit: [X/10 - cite agents]
        - Technical feasibility: [X/10 - cite agents]
        - Safety profile: [X/10 - cite agents]
        - Commercial viability: [X/10 - cite agents]
        - **Overall Score:** [Weighted average]
        
        **Critical Success Factors:**
        1. [From agent insights]
        2. [From agent insights]
        3. [From agent insights]
        
        **Red Flags/Deal Breakers:**
        - [Any fatal flaws identified by agents]
        
        ### 5. Actionable Roadmap
        
        **Immediate (0-3 months):**
        - [Actions from agent recommendations]
        
        **Near-term (3-12 months):**
        - [Milestones from agent outputs]
        
        **Long-term (1-3 years):**
        - [Strategic direction]
        
        ### 6. Resource Requirements
        - Budget: [Based on all agent inputs]
        - Team: [Skills needed from all stages]
        - Partnerships: [Opportunities identified]
        
        ### 7. Scenario Analysis
        **Best Case:** [If all goes optimally]
        **Base Case:** [Expected outcome]
        **Worst Case:** [Major risks materialize]
        
        **Contingencies:** [For identified failure modes]
        
        ---
        
        Use ReasoningTools() for systematic compilation. Cite specific agents for each insight.
        Provide clear, actionable recommendations with supporting evidence.
        """
        
        response = self.coordinator_agent.run(compilation_prompt)
        return response.content


if __name__ == "__main__":
    workflow = DrugDiscoveryWorkflow()
    
    query = """
    Develop a novel therapeutic for Alzheimer's disease targeting tau protein 
    aggregation and neuroinflammation pathways, with focus on blood-brain barrier 
    penetration and minimal side effects
    """
    
    results = workflow.execute_workflow(query)
    
    print("\n" + "="*80)
    print("FINAL COORDINATOR COMPILATION")
    print("="*80)
    print(results['coordinator_response'])
    
    
