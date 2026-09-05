"""
Main Orchestrator for Medical Research Pipeline.

This module provides the main entry point for the research pipeline,
combining Agno agents and LangGraph workflows into a cohesive system.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import google.generativeai as genai

from .config import api_config, research_config, agent_config
from .tools.research_tools import (
    create_default_tool_registry,
    ToolRegistry,
    ResearchContext
)
from .agents.agno_agents import (
    AgentTeam,
    create_agent_team,
    create_single_agent
)
from .workflows.langgraph_workflow import (
    ResearchWorkflowGraph,
    create_research_workflow,
    create_streaming_runner,
    ResearchState
)
from .schemas import (
    DeepResearchStructuredOutput, PaperResult, ClinicalTrialResult,
    DrugResult, EvidenceSummary, ResearchGap, Recommendation,
    CritiqueResult, KeyFinding, TherapeuticLandscape
)


class MedicalResearchPipeline:
    """
    Main orchestrator for the medical research pipeline.
    
    This class provides:
    - High-level API for research queries
    - Integration of Agno agents with LangGraph workflows
    - Multiple execution modes (quick, standard, comprehensive)
    - Report generation and export
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        pubmed_api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None
    ):
        # Initialize Gemini API client
        self.api_key = google_api_key or api_config.google_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.llm_client = genai.GenerativeModel(api_config.primary_model)
        else:
            self.llm_client = None
        
        # Initialize tools
        self.tool_registry = create_default_tool_registry(
            pubmed_api_key=pubmed_api_key or api_config.pubmed_api_key,
            tavily_api_key=tavily_api_key or api_config.tavily_api_key
        )
        
        # Initialize agent team
        self.agent_team = create_agent_team(
            llm_client=self.llm_client,
            tool_registry=self.tool_registry
        )
        
        # Initialize workflow
        self.workflow = create_research_workflow(
            agents={
                "coordinator": self.agent_team.coordinator,
                "literature": self.agent_team.literature_agent,
                "trials": self.agent_team.trials_agent,
                "drugs": self.agent_team.drug_agent,
                "synthesis": self.agent_team.synthesis_agent,
                "critic": self.agent_team.critic_agent
            },
            tools={name: self.tool_registry.get(name) for name in self.tool_registry.list_tools()}
        )
        
        # Research history
        self.research_history: List[Dict[str, Any]] = []
    
    async def research(
        self,
        query: str,
        mode: str = "comprehensive",
        include_clinical_trials: bool = True,
        include_drug_info: bool = True,
        output_format: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Execute a research query.
        
        Args:
            query: The research question
            mode: Research mode ("quick", "standard", "comprehensive")
            include_clinical_trials: Whether to search clinical trials
            include_drug_info: Whether to include drug information
            output_format: Output format ("summary", "detailed", "full")
            
        Returns:
            Research results with synthesis and recommendations
        """
        
        print(f"\n{'='*60}")
        print(f"Starting Medical Research Pipeline")
        print(f"Query: {query}")
        print(f"Mode: {mode}")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        
        # Configure user preferences
        user_preferences = {
            "include_clinical_trials": include_clinical_trials,
            "include_drug_info": include_drug_info,
            "output_format": output_format,
            "max_papers": research_config.max_papers_per_query,
            "max_trials": research_config.max_clinical_trials
        }
        
        # Execute workflow
        result_state = await self.workflow.run(
            query=query,
            research_type=mode,
            user_preferences=user_preferences
        )
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Format results
        results = self._format_results(result_state, output_format, execution_time)
        
        # Store in history
        self.research_history.append({
            "query": query,
            "timestamp": start_time.isoformat(),
            "mode": mode,
            "execution_time": execution_time,
            "results_summary": results.get("summary", "")
        })
        
        print(f"\n{'='*60}")
        print(f"Research Complete in {execution_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return results
    
    async def research_with_streaming(
        self,
        query: str,
        mode: str = "comprehensive",
        callback: Optional[callable] = None
    ):
        """
        Execute research with streaming updates.
        
        Yields intermediate results for real-time progress tracking.
        """
        
        runner = create_streaming_runner(self.workflow)
        
        if callback:
            runner.add_callback(callback)
        
        async for update in runner.run_with_streaming(query, mode):
            yield update
    
    async def quick_search(self, query: str) -> Dict[str, Any]:
        """Quick literature search without full analysis."""
        
        pubmed_tool = self.tool_registry.get("pubmed_search")
        if pubmed_tool:
            papers = await pubmed_tool.execute(query=query, max_results=10)
            return {
                "query": query,
                "papers": [p.model_dump() if hasattr(p, 'model_dump') else p for p in papers],
                "count": len(papers)
            }
        return {"error": "PubMed tool not available"}
    
    async def analyze_drug(self, drug_name: str) -> Dict[str, Any]:
        """Quick drug information lookup."""
        
        drug_agent = self.agent_team.drug_agent
        return await drug_agent.get_drug_info(drug_name, include_interactions=True)
    
    async def find_clinical_trials(
        self,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        status: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search for clinical trials."""
        
        trials_agent = self.agent_team.trials_agent
        return await trials_agent.analyze_trials(
            condition=condition,
            intervention=intervention,
            phase=status
        )
    
    def _format_results(
        self,
        state: ResearchState,
        output_format: str,
        execution_time: float
    ) -> Dict[str, Any]:
        """Format results based on output format."""
        
        # Generate structured output
        structured_output = self._generate_structured_output(state, execution_time)
        
        if output_format == "summary":
            return {
                "query": state["query"],
                "summary": self._generate_summary(state),
                "key_findings": self._extract_key_findings(state),
                "execution_time": execution_time,
                "structured_output": structured_output.model_dump()
            }
        
        elif output_format == "detailed":
            return {
                "query": state["query"],
                "summary": self._generate_summary(state),
                "synthesis": state["synthesis"],
                "literature_count": len(state["literature_results"]),
                "trials_count": len(state["clinical_trial_results"]),
                "drugs_count": len(state["drug_results"]),
                "gaps": state["gaps_identified"],
                "recommendations": state["recommendations"],
                "quality_score": state["critique_results"].get("quality_score"),
                "execution_time": execution_time,
                "structured_output": structured_output.model_dump()
            }
        
        else:  # full
            return {
                "query": state["query"],
                "research_plan": state["research_plan"],
                "literature_results": state["literature_results"],
                "clinical_trial_results": state["clinical_trial_results"],
                "drug_results": state["drug_results"],
                "synthesis": state["synthesis"],
                "gaps_identified": state["gaps_identified"],
                "recommendations": state["recommendations"],
                "critique_results": state["critique_results"],
                "phase_history": state["phase_history"],
                "execution_time": execution_time,
                "messages": state["messages"],
                "structured_output": structured_output.model_dump()
            }
    
    def _generate_structured_output(
        self, 
        state: ResearchState, 
        execution_time: float
    ) -> DeepResearchStructuredOutput:
        """Generate comprehensive structured output from research state."""
        
        import uuid
        
        # Parse papers into structured format
        papers = []
        for p in state.get("literature_results", []):
            try:
                papers.append(PaperResult(
                    title=p.get("title", "Unknown"),
                    pmid=p.get("pmid"),
                    doi=p.get("doi"),
                    authors=p.get("authors", []),
                    journal=p.get("journal"),
                    publication_date=p.get("publication_date"),
                    abstract=p.get("abstract"),
                    url=p.get("url"),
                    citation_count=p.get("citation_count"),
                    keywords=p.get("keywords", []),
                    study_type=p.get("study_type"),
                    evidence_level=p.get("evidence_level")
                ))
            except Exception:
                pass
        
        # Parse trials into structured format
        trials = []
        active_count = 0
        for t in state.get("clinical_trial_results", []):
            try:
                status = t.get("status", "Unknown")
                if "RECRUITING" in status.upper() or "ACTIVE" in status.upper():
                    active_count += 1
                trials.append(ClinicalTrialResult(
                    nct_id=t.get("nct_id", "Unknown"),
                    title=t.get("title", "Unknown"),
                    status=status,
                    phase=t.get("phase"),
                    conditions=t.get("conditions", []),
                    interventions=t.get("interventions", []),
                    sponsor=t.get("sponsor"),
                    start_date=t.get("start_date"),
                    completion_date=t.get("completion_date"),
                    enrollment=t.get("enrollment"),
                    primary_outcomes=t.get("primary_outcomes", []),
                    url=t.get("url"),
                    locations=t.get("locations", [])
                ))
            except Exception:
                pass
        
        # Parse drugs into structured format
        drugs = []
        for d in state.get("drug_results", []):
            try:
                drugs.append(DrugResult(
                    name=d.get("name", d.get("generic_name", "Unknown")),
                    generic_name=d.get("generic_name"),
                    brand_names=d.get("brand_names", []),
                    drug_class=d.get("drug_class"),
                    mechanism=d.get("mechanism"),
                    fda_status=d.get("fda_status"),
                    approval_date=d.get("approval_date"),
                    indications=d.get("indications", []),
                    contraindications=d.get("contraindications", []),
                    side_effects=d.get("side_effects", []),
                    interactions=d.get("interactions", []),
                    dosage_forms=d.get("dosage_forms", [])
                ))
            except Exception:
                pass
        
        # Create evidence summary
        evidence_summary = EvidenceSummary(
            total_papers=len(papers),
            total_trials=len(trials),
            total_drugs=len(drugs),
            meta_analyses_count=sum(1 for p in papers if p.study_type and "meta" in p.study_type.lower()),
            rct_count=sum(1 for p in papers if p.study_type and "rct" in p.study_type.lower()),
            overall_evidence_quality="Moderate" if len(papers) > 5 else "Low",
            confidence_level=0.7 if len(papers) > 10 else 0.5
        )
        
        # Parse research gaps
        research_gaps = []
        for i, gap in enumerate(state.get("gaps_identified", [])):
            research_gaps.append(ResearchGap(
                gap_description=gap,
                gap_type="knowledge",
                priority="High" if i < 2 else "Medium",
                suggested_research=f"Conduct further research on: {gap}"
            ))
        
        # Parse recommendations
        recommendations = []
        for rec in state.get("recommendations", []):
            recommendations.append(Recommendation(
                recommendation=rec,
                target_audience="clinicians",
                strength="Moderate",
                evidence_basis="Based on systematic literature review"
            ))
        
        # Parse critique
        critique_data = state.get("critique_results", {})
        critique = CritiqueResult(
            quality_score=critique_data.get("quality_score", 7.0),
            completeness_score=critique_data.get("completeness_score"),
            accuracy_score=critique_data.get("accuracy_score"),
            structure_score=critique_data.get("structure_score"),
            clinical_relevance_score=critique_data.get("clinical_relevance_score"),
            overall_assessment=critique_data.get("overall_assessment", "Satisfactory"),
            strengths=critique_data.get("strengths", []),
            weaknesses=critique_data.get("weaknesses", []),
            suggestions=critique_data.get("improvements_suggested", [])
        )
        
        # Generate key findings
        key_findings = []
        if papers:
            key_findings.append(KeyFinding(
                finding=f"Found {len(papers)} relevant peer-reviewed papers",
                source_type="literature",
                confidence="High",
                supporting_evidence=[p.title for p in papers[:3]]
            ))
        if trials:
            key_findings.append(KeyFinding(
                finding=f"Identified {len(trials)} clinical trials, {active_count} actively recruiting",
                source_type="clinical_trial",
                confidence="High",
                supporting_evidence=[t.nct_id for t in trials[:3]]
            ))
        if drugs:
            key_findings.append(KeyFinding(
                finding=f"Analyzed {len(drugs)} therapeutic options",
                source_type="drug_data",
                confidence="High",
                supporting_evidence=[d.name for d in drugs[:3]]
            ))
        
        # Generate therapeutic landscape
        therapeutic_landscape = TherapeuticLandscape(
            current_standard_of_care="See synthesis for current treatment options",
            emerging_therapies=[d.name for d in drugs if d.fda_status and "approved" not in d.fda_status.lower()][:5],
            pipeline_drugs=[t.interventions[0] if t.interventions else "Unknown" for t in trials if t.phase and "3" in t.phase][:5],
            unmet_needs=[gap.gap_description for gap in research_gaps[:3]],
            market_trends="Growing research interest based on publication trends"
        )
        
        # Generate executive summary
        executive_summary = f"""Research synthesis for "{state['query']}" analyzed {len(papers)} peer-reviewed papers, 
{len(trials)} clinical trials ({active_count} active), and {len(drugs)} therapeutic options. 
Key findings indicate {"promising developments in the field" if len(papers) > 5 else "limited available evidence"}. 
{len(research_gaps)} research gaps were identified requiring further investigation."""
        
        return DeepResearchStructuredOutput(
            research_id=str(uuid.uuid4()),
            query=state["query"],
            mode=state.get("research_type", "comprehensive"),
            status="complete",
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            papers=papers,
            papers_summary=f"Found {len(papers)} relevant papers from PubMed",
            trials=trials,
            trials_summary=f"Found {len(trials)} clinical trials, {active_count} actively recruiting",
            active_trials_count=active_count,
            drugs=drugs,
            drugs_summary=f"Analyzed {len(drugs)} therapeutic options",
            evidence_summary=evidence_summary,
            key_findings=key_findings,
            therapeutic_landscape=therapeutic_landscape,
            executive_summary=executive_summary,
            synthesis=state.get("synthesis"),
            research_gaps=research_gaps,
            recommendations=recommendations,
            critique=critique,
            clinical_implications=state.get("recommendations", [])[:3],
            future_directions=[gap.suggested_research for gap in research_gaps[:3] if gap.suggested_research]
        )
    
    def _generate_summary(self, state: ResearchState) -> str:
        """Generate a brief summary of results."""
        
        return f"""Research on "{state['query']}" found {len(state['literature_results'])} papers, 
{len(state['clinical_trial_results'])} clinical trials, and {len(state['drug_results'])} drug entries. 
{len(state['gaps_identified'])} research gaps were identified."""
    
    def _extract_key_findings(self, state: ResearchState) -> List[str]:
        """Extract key findings from synthesis."""
        
        findings = []
        
        if state["literature_results"]:
            findings.append(f"Found {len(state['literature_results'])} relevant research papers")
        
        if state["clinical_trial_results"]:
            findings.append(f"Identified {len(state['clinical_trial_results'])} clinical trials")
        
        if state["gaps_identified"]:
            findings.extend(state["gaps_identified"])
        
        return findings
    
    def export_results(
        self,
        results: Dict[str, Any],
        filepath: str,
        format: str = "json"
    ) -> None:
        """Export results to file."""
        
        path = Path(filepath)
        
        if format == "json":
            with open(path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        elif format == "markdown":
            md_content = self._results_to_markdown(results)
            with open(path, 'w') as f:
                f.write(md_content)
        
        elif format == "html":
            html_content = self._results_to_html(results)
            with open(path, 'w') as f:
                f.write(html_content)
        
        print(f"Results exported to {filepath}")
    
    def _results_to_markdown(self, results: Dict[str, Any]) -> str:
        """Convert results to Markdown format."""
        
        md = f"""# Medical Research Report

## Query
{results.get('query', 'N/A')}

## Summary
{results.get('summary', 'N/A')}

## Synthesis
{results.get('synthesis', 'N/A')}

## Statistics
- Papers found: {results.get('literature_count', 0)}
- Clinical trials: {results.get('trials_count', 0)}
- Drugs analyzed: {results.get('drugs_count', 0)}

## Research Gaps
{chr(10).join(f'- {gap}' for gap in results.get('gaps', []))}

## Recommendations
{chr(10).join(f'- {rec}' for rec in results.get('recommendations', []))}

## Quality Assessment
Score: {results.get('quality_score', 'N/A')}

---
*Generated by Medical Research Pipeline*
*Execution time: {results.get('execution_time', 0):.2f} seconds*
"""
        return md
    
    def _results_to_html(self, results: Dict[str, Any]) -> str:
        """Convert results to HTML format."""
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Medical Research Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; color: #3498db; }}
        .synthesis {{ background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        ul {{ line-height: 1.8; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <h1>Medical Research Report</h1>
    
    <h2>Research Query</h2>
    <p><strong>{results.get('query', 'N/A')}</strong></p>
    
    <h2>Summary</h2>
    <p>{results.get('summary', 'N/A')}</p>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{results.get('literature_count', 0)}</div>
            <div>Papers Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{results.get('trials_count', 0)}</div>
            <div>Clinical Trials</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{results.get('drugs_count', 0)}</div>
            <div>Drugs Analyzed</div>
        </div>
    </div>
    
    <h2>Synthesis</h2>
    <div class="synthesis">
        <pre>{results.get('synthesis', 'N/A')}</pre>
    </div>
    
    <h2>Research Gaps</h2>
    <ul>
        {''.join(f'<li>{gap}</li>' for gap in results.get('gaps', []))}
    </ul>
    
    <h2>Recommendations</h2>
    <ul>
        {''.join(f'<li>{rec}</li>' for rec in results.get('recommendations', []))}
    </ul>
    
    <div class="footer">
        <p>Generated by Medical Research Pipeline</p>
        <p>Execution time: {results.get('execution_time', 0):.2f} seconds</p>
    </div>
</body>
</html>
"""
        return html
    
    def show_workflow_graph(self) -> None:
        """Display the workflow graph visualization."""
        print(self.workflow.visualize())
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get research history."""
        return self.research_history


# ============================================================================
# Convenience Functions
# ============================================================================

async def run_research(
    query: str,
    mode: str = "comprehensive",
    google_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run research with minimal setup.
    
    Args:
        query: Research question
        mode: Research mode
        google_api_key: Optional API key (uses env var if not provided)
        
    Returns:
        Research results
    """
    
    pipeline = MedicalResearchPipeline(google_api_key=google_api_key)
    return await pipeline.research(query, mode=mode)


def create_pipeline(
    google_api_key: Optional[str] = None,
    pubmed_api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None
) -> MedicalResearchPipeline:
    """Create a configured research pipeline."""
    
    return MedicalResearchPipeline(
        google_api_key=google_api_key,
        pubmed_api_key=pubmed_api_key,
        tavily_api_key=tavily_api_key
    )


# ============================================================================
# CLI Interface
# ============================================================================

async def main():    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Medical Research Pipeline - Deep Research for Healthcare"
    )
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        help="Research query"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="comprehensive",
        help="Research mode"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown", "html"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="Show workflow graph"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    pipeline = create_pipeline()
    
    if args.show_graph:
        pipeline.show_workflow_graph()
        return
    
    if args.interactive:
        print("Medical Research Pipeline - Interactive Mode")
        print("Type 'quit' to exit, 'graph' to show workflow\n")
        
        while True:
            query = input("Enter research query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'graph':
                pipeline.show_workflow_graph()
                continue
            elif not query:
                continue
            
            results = await pipeline.research(query, mode=args.mode)
            print(f"\n{json.dumps(results, indent=2, default=str)}\n")
    
    elif args.query:
        results = await pipeline.research(args.query, mode=args.mode)
        
        if args.output:
            pipeline.export_results(results, args.output, args.format)
        else:
            print(json.dumps(results, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
