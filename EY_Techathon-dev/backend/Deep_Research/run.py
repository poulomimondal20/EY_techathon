import asyncio
from datetime import datetime
from openai import AsyncOpenAI
from config import api_config
from tools.research_tools import create_default_tool_registry
from agents.agno_agents import create_agent_team
from workflows.langgraph_workflow import create_research_workflow


class DeepResearchPipeline:
    def __init__(self):
        self.llm_client = AsyncOpenAI(api_key=api_config.openai_api_key) if api_config.openai_api_key else None
        self.tool_registry = create_default_tool_registry(
            pubmed_api_key=api_config.pubmed_api_key,
            tavily_api_key=api_config.tavily_api_key
        )
        self.agent_team = create_agent_team(llm_client=self.llm_client, tool_registry=self.tool_registry)
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

    async def research(self, query: str) -> dict:
        print(f"\n{'='*70}")
        print(f" DEEP MEDICAL RESEARCH PIPELINE")
        print(f"{'='*70}")
        print(f" Query: {query}")
        print(f"{'='*70}\n")
        
        start_time = datetime.now()
        
        result_state = await self.workflow.run(
            query=query,
            research_type="comprehensive",
            user_preferences={"include_clinical_trials": True, "include_drug_info": True, "output_format": "full"}
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print(f" Research Complete in {execution_time:.2f} seconds")
        print(f"{'='*70}\n")
        
        return {
            "query": result_state["query"],
            "papers": result_state["literature_results"],
            "trials": result_state["clinical_trial_results"],
            "drugs": result_state["drug_results"],
            "synthesis": result_state["synthesis"],
            "gaps": result_state["gaps_identified"],
            "recommendations": result_state["recommendations"],
            "critique": result_state["critique_results"],
            "execution_time": execution_time
        }

    def print_results(self, results: dict):
        print("\n" + "="*70)
        print(" RESEARCH RESULTS")
        print("="*70)
        
        # Stats
        print(f"\n Statistics:")
        print(f"   • Papers found: {len(results['papers'])}")
        print(f"   • Clinical trials: {len(results['trials'])}")
        print(f"   • Drugs analyzed: {len(results['drugs'])}")
        
        # Sources Section
        print("\n" + "-"*70)
        print(" SOURCES - LITERATURE")
        print("-"*70)
        for i, paper in enumerate(results['papers'][:15], 1):
            title = paper.get('title', 'Unknown')
            pmid = paper.get('pmid', 'N/A')
            journal = paper.get('journal', 'Unknown')
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            print(f"\n[{i}] {title}")
            print(f"     Journal: {journal}")
            print(f"     PMID: {pmid} | URL: {url}")
        
        if results['trials']:
            print("\n" + "-"*70)
            print("🔬 SOURCES - CLINICAL TRIALS")
            print("-"*70)
            for i, trial in enumerate(results['trials'][:10], 1):
                title = trial.get('title', 'Unknown')
                nct_id = trial.get('nct_id', 'N/A')
                status = trial.get('status', 'Unknown')
                phase = trial.get('phase', 'N/A')
                url = f"https://clinicaltrials.gov/study/{nct_id}"
                print(f"\n[{i}] {title}")
                print(f"    🏷️  NCT ID: {nct_id} | Status: {status} | Phase: {phase}")
                print(f"    🔗 URL: {url}")
        
        if results['drugs']:
            print("\n" + "-"*70)
            print("💊 SOURCES - DRUGS/THERAPEUTICS")
            print("-"*70)
            for i, drug in enumerate(results['drugs'][:10], 1):
                name = drug.get('name', drug.get('generic_name', 'Unknown'))
                brand = ', '.join(drug.get('brand_names', [])[:3]) or 'N/A'
                mechanism = drug.get('mechanism', 'N/A')[:100]
                fda_status = drug.get('fda_status', 'N/A')
                print(f"\n[{i}] {name}")
                print(f"    💼 Brand: {brand} | FDA: {fda_status}")
                print(f"    ⚙️  Mechanism: {mechanism}...")
        
        # AI Synthesis
        print("\n" + "="*70)
        print(" AI-POWERED SYNTHESIS")
        print("="*70)
        print(results['synthesis'])
        
        # Gaps
        if results['gaps']:
            print("\n" + "-"*70)
            print(" IDENTIFIED RESEARCH GAPS")
            print("-"*70)
            for gap in results['gaps']:
                print(f"  • {gap}")
        
        # Recommendations
        if results['recommendations']:
            print("\n" + "-"*70)
            print(" RECOMMENDATIONS")
            print("-"*70)
            for rec in results['recommendations']:
                print(f"  • {rec}")
        
        # Critique
        critique = results.get('critique', {})
        if critique:
            print("\n" + "-"*70)
            print(" QUALITY ASSESSMENT")
            print("-"*70)
            print(f"   Quality Score: {critique.get('quality_score', 'N/A')}/10")
            if critique.get('overall_assessment'):
                print(f"   Assessment: {critique.get('overall_assessment')}")


async def main():
    print("\n" + "="*70)
    print(" MEDICAL DEEP RESEARCH PIPELINE")
    print("="*70)
    print("Enter your research query (or 'quit' to exit)")
    print("="*70 + "\n")
    
    pipeline = DeepResearchPipeline()
    
    while True:
        query = input("\n Research Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! ")
            break
        
        if not query:
            print("Please enter a valid query.")
            continue
        
        try:
            results = await pipeline.research(query)
            pipeline.print_results(results)
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
