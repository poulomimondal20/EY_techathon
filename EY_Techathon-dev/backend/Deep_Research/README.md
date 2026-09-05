# Medical Research Pipeline

A comprehensive agentic AI system for deep medical and pharmaceutical research, combining **Agno-style agents** with **LangGraph workflows** for sophisticated research automation.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MEDICAL RESEARCH PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        ORCHESTRATOR                                  │   │
│  │   • Main entry point                                                │   │
│  │   • Coordinates agents and workflows                                │   │
│  │   • Handles input/output formatting                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                          │
│                  ┌───────────────┴───────────────┐                          │
│                  ▼                               ▼                          │
│  ┌─────────────────────────┐     ┌─────────────────────────────────────┐   │
│  │     AGNO AGENTS         │     │      LANGGRAPH WORKFLOW             │   │
│  │                         │     │                                     │   │
│  │  ┌─────────────────┐   │     │  ┌─────────┐    ┌─────────────┐    │   │
│  │  │  Coordinator    │   │     │  │Planning │───▶│ Literature  │    │   │
│  │  └─────────────────┘   │     │  └─────────┘    │   Search    │    │   │
│  │  ┌─────────────────┐   │     │                 └──────┬──────┘    │   │
│  │  │  Literature     │   │     │                        │           │   │
│  │  │  Specialist     │   │     │       ┌───────────────┼───────┐   │   │
│  │  └─────────────────┘   │     │       ▼               ▼       ▼   │   │
│  │  ┌─────────────────┐   │     │  ┌─────────┐   ┌──────────┐  │   │   │
│  │  │  Clinical Trials│   │     │  │ Trials  │   │  Drugs   │──┘   │   │
│  │  │  Analyst        │   │     │  └────┬────┘   └────┬─────┘      │   │
│  │  └─────────────────┘   │     │       └──────┬──────┘            │   │
│  │  ┌─────────────────┐   │     │              ▼                   │   │
│  │  │  Drug Info      │   │     │       ┌────────────┐             │   │
│  │  │  Specialist     │   │     │       │ Synthesis  │             │   │
│  │  └─────────────────┘   │     │       └─────┬──────┘             │   │
│  │  ┌─────────────────┐   │     │             ▼                    │   │
│  │  │  Synthesizer    │   │     │       ┌────────────┐             │   │
│  │  └─────────────────┘   │     │       │  Critique  │◄────┐       │   │
│  │  ┌─────────────────┐   │     │       └─────┬──────┘     │       │   │
│  │  │  Critic         │   │     │        ┌────┴────┐       │       │   │
│  │  └─────────────────┘   │     │        ▼         ▼       │       │   │
│  └─────────────────────────┘     │   ┌────────┐ ┌────────┐ │       │   │
│                                  │   │Revision│─│Complete│─┘       │   │
│  ┌─────────────────────────┐     │   └────────┘ └────────┘         │   │
│  │     RESEARCH TOOLS      │     └─────────────────────────────────────┘   │
│  │                         │                                               │
│  │  • PubMed Search        │                                               │
│  │  • Clinical Trials API  │                                               │
│  │  • OpenFDA Drug DB      │                                               │
│  │  • Web Search           │                                               │
│  │  • Literature Synthesis │                                               │
│  └─────────────────────────┘                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### Agno Agents
- **Research Coordinator**: Plans and orchestrates research tasks
- **Literature Search Specialist**: Expert in PubMed queries and paper analysis
- **Clinical Trials Analyst**: Searches and analyzes clinical trials
- **Drug Information Specialist**: Comprehensive drug database queries
- **Research Synthesizer**: Integrates findings into coherent reports
- **Research Critic**: Quality control and improvement suggestions

### LangGraph Workflow
- State machine-based execution
- Conditional routing based on research needs
- Parallel execution of independent tasks
- Automatic quality critique and revision loop
- Streaming updates for real-time progress

### Research Tools
- **PubMed Search**: Access to 35M+ medical publications
- **ClinicalTrials.gov**: 400K+ clinical trials database
- **OpenFDA**: Drug labels, adverse events, recalls
- **Web Search**: Latest news via Tavily/Serper APIs

## 📦 Installation

```bash
cd medical_research_pipeline
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
PUBMED_API_KEY=your_pubmed_api_key  # Optional, but recommended
TAVILY_API_KEY=your_tavily_api_key  # For web search
SERPER_API_KEY=your_serper_api_key  # Alternative web search
```

## 🔧 Usage

### Basic Research

```python
import asyncio
from medical_research_pipeline import create_pipeline

async def main():
    # Create pipeline
    pipeline = create_pipeline()
    
    # Execute research
    results = await pipeline.research(
        query="What are the latest CAR-T cell therapies for lymphoma?",
        mode="comprehensive",
        include_clinical_trials=True,
        include_drug_info=True
    )
    
    print(results["synthesis"])

asyncio.run(main())
```

### Quick Literature Search

```python
pipeline = create_pipeline()
papers = await pipeline.quick_search("CRISPR gene editing safety")
print(f"Found {papers['count']} papers")
```

### Streaming Research with Progress Updates

```python
async for update in pipeline.research_with_streaming(
    "Novel Alzheimer's treatments",
    mode="comprehensive"
):
    if update["type"] == "intermediate":
        print(f"Progress: {update['node']} -> {update['state']['current_phase']}")
    elif update["type"] == "complete":
        print("Research complete!")
```

### Export Results

```python
results = await pipeline.research("Immunotherapy in melanoma")

pipeline.export_results(results, "report.json", format="json")
pipeline.export_results(results, "report.md", format="markdown")
pipeline.export_results(results, "report.html", format="html")
```

### CLI Usage

```bash
# Comprehensive research
python -m medical_research_pipeline "Your research query here"

# Quick mode
python -m medical_research_pipeline "Your query" --mode quick

# Export to markdown
python -m medical_research_pipeline "Your query" --output report.md --format markdown

# Show workflow graph
python -m medical_research_pipeline --show-graph

# Interactive mode
python -m medical_research_pipeline --interactive
```

## 📁 Project Structure

```
medical_research_pipeline/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── orchestrator.py          # Main orchestrator/pipeline
├── requirements.txt         # Python dependencies
├── examples.py              # Usage examples
├── README.md                # This file
│
├── agents/
│   ├── __init__.py
│   └── agno_agents.py       # Agno-style agent implementations
│
├── workflows/
│   ├── __init__.py
│   └── langgraph_workflow.py  # LangGraph workflow definitions
│
└── tools/
    ├── __init__.py
    └── research_tools.py    # Research tool implementations
```

## 🔄 Workflow Phases

1. **Planning**: Analyze query and create research plan
2. **Literature Search**: Search PubMed for relevant papers
3. **Clinical Trials** (optional): Search ClinicalTrials.gov
4. **Drug Analysis** (optional): Query drug databases
5. **Synthesis**: Combine all findings into coherent report
6. **Critique**: Quality assessment of the synthesis
7. **Revision** (if needed): Improve based on critique
8. **Complete**: Finalize and return results

## 🎯 Research Modes

| Mode | Description | Papers | Trials | Speed |
|------|-------------|--------|--------|-------|
| `quick` | Fast overview | 10 | 5 | ~30s |
| `standard` | Balanced research | 15 | 10 | ~60s |
| `comprehensive` | Deep analysis | 20+ | 15+ | ~120s |

## 🔐 API Keys

| API | Required | Free Tier | Purpose |
|-----|----------|-----------|---------|
| OpenAI | Yes | No | LLM for agents |
| PubMed | Recommended | Yes | Literature search |
| Tavily | Optional | Yes (limited) | Web search |
| Serper | Optional | Yes (limited) | Alternative web search |

## 📊 Output Formats

### Summary Format
```json
{
  "query": "...",
  "summary": "...",
  "key_findings": ["..."],
  "execution_time": 45.2
}
```

### Detailed Format
```json
{
  "query": "...",
  "synthesis": "...",
  "literature_count": 15,
  "trials_count": 8,
  "gaps": ["..."],
  "recommendations": ["..."],
  "quality_score": 8.5
}
```

### Full Format
Complete state with all intermediate results, messages, and execution history.

## 🛠️ Customization

### Add Custom Agent

```python
from medical_research_pipeline.agents import BaseAgent, AgentConfig, AgentRole

class MyCustomAgent(BaseAgent):
    def __init__(self, llm_client=None, tool_registry=None):
        config = AgentConfig(
            name="Custom Specialist",
            role=AgentRole.SPECIALIST,
            description="My custom research agent",
            system_prompt="You are a specialist in...",
            tools=["pubmed_search", "web_search"]
        )
        super().__init__(config, llm_client, tool_registry)
```

### Add Custom Tool

```python
from medical_research_pipeline.tools import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "My custom research tool"
    
    async def execute(self, **kwargs):
        # Your tool logic here
        return results
```

## ⚠️ Limitations

- API rate limits may affect performance
- Medical information is for research purposes only
- Always verify findings with authoritative sources
- Not a substitute for professional medical advice

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read the contributing guidelines first.

---

*Built with ❤️ for the medical research community*
