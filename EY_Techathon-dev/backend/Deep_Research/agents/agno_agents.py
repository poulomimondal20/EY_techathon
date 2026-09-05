"""
Agno-based Agents for Medical Research Pipeline.

This module implements specialized AI agents using the Agno framework for:
- Research Planning & Coordination
- Literature Search & Analysis
- Clinical Trials Analysis
- Drug Information Specialist
- Synthesis & Report Generation
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import os
from datetime import datetime

from pydantic import BaseModel, Field

try:
    from agno.agent import Agent
    from agno.models.google import Gemini
    from agno.tools import tool
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    print("Warning: Agno not installed. Using fallback implementation.")

# Agno-style agent implementation
# Uses Agno framework when available, falls back to Gemini direct API otherwise


class AgentRole(Enum):
    """Roles for different agent types."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    SYNTHESIZER = "synthesizer"
    CRITIC = "critic"
    SPECIALIST = "specialist"


class Message(BaseModel):
    """Message structure for agent communication."""
    
    role: str  # "user", "assistant", "system", "tool"
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """State object for agent execution."""
    
    messages: List[Message] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    memory: Dict[str, Any] = Field(default_factory=dict)
    current_task: Optional[str] = None
    completed_tasks: List[str] = Field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 10
    should_stop: bool = False
    error: Optional[str] = None


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    name: str
    role: AgentRole
    description: str
    system_prompt: str
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: List[str] = Field(default_factory=list)
    memory_enabled: bool = True
    reflection_enabled: bool = False


# ============================================================================
# Base Agent Class (Agno-style)
# ============================================================================

class BaseAgent:
    """
    Base agent class following Agno patterns.
    
    Agno agents are:
    - Stateful with memory
    - Tool-enabled
    - Capable of multi-step reasoning
    - Able to reflect and improve
    """
    
    def __init__(
        self,
        config: AgentConfig,
        llm_client: Any = None,
        tool_registry: Any = None
    ):
        self.config = config
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.state = AgentState()
        self._agno_agent = None
        
        # Initialize Agno agent if available
        if AGNO_AVAILABLE and llm_client:
            self._init_agno_agent()
    
    def _init_agno_agent(self):
        """Initialize the Agno agent with Gemini model."""
        try:
            self._agno_agent = Agent(
                name=self.config.name,
                model=Gemini(id=self.config.model),
                instructions=self.config.system_prompt,
                markdown=True,
            )
        except Exception as e:
            print(f"Warning: Could not initialize Agno agent: {e}")
            self._agno_agent = None
        
    @property
    def name(self) -> str:
        return self.config.name
    
    @property
    def role(self) -> AgentRole:
        return self.config.role
        
    def reset(self) -> None:
        """Reset agent state."""
        self.state = AgentState()
        
    async def think(self, input_message: str) -> str:
        """
        Main thinking loop - process input and generate response.
        This is the core Agno agent execution pattern.
        """
        # Add input to messages
        self.state.messages.append(Message(
            role="user",
            content=input_message
        ))
        
        # Use Agno agent if available
        if self._agno_agent:
            try:
                response = await self._generate_agno_response(input_message)
                self.state.messages.append(Message(
                    role="assistant",
                    content=response,
                    name=self.name
                ))
                self.state.should_stop = True
                return response
            except Exception as e:
                print(f"Agno agent error, falling back: {e}")
        
        while not self.state.should_stop and self.state.iteration < self.state.max_iterations:
            self.state.iteration += 1
            
            # Generate response with LLM
            response = await self._generate_response()
            
            # Check for tool calls
            if response.get("tool_calls"):
                # Execute tools
                tool_results = await self._execute_tools(response["tool_calls"])
                
                # Add tool results to messages
                for result in tool_results:
                    self.state.messages.append(Message(
                        role="tool",
                        content=json.dumps(result["result"]),
                        tool_call_id=result["tool_call_id"]
                    ))
            else:
                # No more tool calls - we have a final response
                final_response = response.get("content", "")
                self.state.messages.append(Message(
                    role="assistant",
                    content=final_response,
                    name=self.name
                ))
                
                # Apply reflection if enabled
                if self.config.reflection_enabled:
                    final_response = await self._reflect(final_response)
                
                self.state.should_stop = True
                return final_response
        
        return "Max iterations reached without conclusion."
    
    async def _generate_agno_response(self, message: str) -> str:
        """Generate response using Agno agent."""
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._agno_agent.run(message)
        )
        # Extract content from Agno response
        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    async def _generate_response(self) -> Dict[str, Any]:
        """Generate response using LLM (Gemini)."""
        
        messages = self._prepare_messages()
        tools = self._prepare_tools()
        
        if self.llm_client:
            # Use Gemini client
            # Combine system prompt and messages into a single prompt
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt_parts.append(f"Instructions: {content}\n")
                elif role == "user":
                    prompt_parts.append(f"User: {content}\n")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}\n")
                elif role == "tool":
                    prompt_parts.append(f"Tool Result: {content}\n")
            
            full_prompt = "\n".join(prompt_parts)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm_client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": self.config.temperature,
                        "max_output_tokens": self.config.max_tokens
                    }
                )
            )
            
            return {
                "content": response.text if response.text else "",
                "tool_calls": None  # Gemini handles tools differently
            }
        else:
            # Fallback for testing without LLM
            return {
                "content": f"[{self.name}] Processing: {self.state.messages[-1].content[:100]}...",
                "tool_calls": None
            }
    
    def _prepare_messages(self) -> List[Dict[str, str]]:
        """Prepare messages for LLM API call."""
        
        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        
        for msg in self.state.messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.name:
                message_dict["name"] = msg.name
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            messages.append(message_dict)
            
        return messages
    
    def _prepare_tools(self) -> Optional[List[Dict]]:
        """Prepare tools for LLM API call."""
        
        if not self.tool_registry or not self.config.tools:
            return None
            
        tools = []
        for tool_name in self.config.tools:
            tool = self.tool_registry.get(tool_name)
            if tool:
                tools.append({
                    "type": "function",
                    "function": tool.to_function_schema()
                })
                
        return tools if tools else None
    
    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute tool calls and return results."""
        
        results = []
        
        for tc in tool_calls:
            tool_name = tc["function"]["name"]
            tool_args = json.loads(tc["function"]["arguments"])
            
            tool = self.tool_registry.get(tool_name) if self.tool_registry else None
            
            if tool:
                try:
                    result = await tool.execute(**tool_args)
                    results.append({
                        "tool_call_id": tc["id"],
                        "tool_name": tool_name,
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "tool_call_id": tc["id"],
                        "tool_name": tool_name,
                        "result": {"error": str(e)}
                    })
            else:
                results.append({
                    "tool_call_id": tc["id"],
                    "tool_name": tool_name,
                    "result": {"error": f"Tool '{tool_name}' not found"}
                })
                
        return results
    
    async def _reflect(self, response: str) -> str:
        """Reflect on and potentially improve the response."""
        
        reflection_prompt = f"""Review your response and consider:
1. Is the information accurate and complete?
2. Are there any gaps or areas that need more detail?
3. Is the response well-structured and clear?

Original response:
{response}

If improvements are needed, provide an improved version. Otherwise, confirm the response is satisfactory."""
        
        # Add reflection to messages temporarily
        self.state.messages.append(Message(role="user", content=reflection_prompt))
        
        if self.llm_client:
            reflection_response = await self._generate_response()
            return reflection_response.get("content", response)
        
        return response
    
    def add_to_memory(self, key: str, value: Any) -> None:
        """Add information to agent memory."""
        self.state.memory[key] = value
        
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent memory."""
        return self.state.memory.get(key)
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """Update agent context."""
        self.state.context.update(context)


# ============================================================================
# Specialized Medical Research Agents
# ============================================================================

class ResearchCoordinatorAgent(BaseAgent):
    """
    Coordinator agent that plans and orchestrates research tasks.
    Breaks down complex research queries into subtasks.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="ResearchCoordinator",
            role=AgentRole.COORDINATOR,
            description="Plans and coordinates medical research tasks",
            system_prompt="""You are a Medical Research Coordinator AI agent. Your role is to:

1. Analyze research queries and break them into subtasks
2. Determine which specialized agents should handle each subtask
3. Create a research plan with clear objectives
4. Coordinate information flow between agents
5. Ensure comprehensive coverage of the research topic

When given a research query, you should:
- Identify the key aspects that need investigation
- Plan literature searches, clinical trial lookups, and drug information queries
- Specify what information each search should focus on
- Define success criteria for the research

Output your plan as a structured JSON with:
{
    "research_topic": "...",
    "objectives": ["..."],
    "subtasks": [
        {
            "id": 1,
            "type": "literature_search|clinical_trial_search|drug_lookup|synthesis",
            "description": "...",
            "parameters": {...}
        }
    ],
    "success_criteria": ["..."]
}""",
            model="gemini-2.0-flash",
            tools=["pubmed_search", "clinical_trials_search", "drug_database"],
            reflection_enabled=True
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def create_research_plan(self, query: str) -> Dict[str, Any]:
        """Create a comprehensive research plan."""
        
        planning_prompt = f"""Create a comprehensive research plan for the following query:

RESEARCH QUERY: {query}

Consider:
1. What literature searches are needed?
2. Should we look at clinical trials?
3. Are there specific drugs or treatments to investigate?
4. What synthesis and analysis is required?

Provide a detailed, actionable research plan."""
        
        response = await self.think(planning_prompt)
        
        # Try to parse as JSON
        try:
            # Find JSON in response
            json_match = response[response.find("{"):response.rfind("}")+1]
            plan = json.loads(json_match)
            self.add_to_memory("current_plan", plan)
            return plan
        except:
            return {
                "research_topic": query,
                "objectives": ["Investigate the research query"],
                "subtasks": [
                    {"id": 1, "type": "literature_search", "description": query}
                ],
                "raw_response": response
            }


class LiteratureSearchAgent(BaseAgent):
    """
    Agent specialized in searching and analyzing medical literature.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="LiteratureSpecialist",
            role=AgentRole.RESEARCHER,
            description="Searches and analyzes medical literature from PubMed and other sources",
            system_prompt="""You are a Medical Literature Search Specialist AI agent. Your expertise is in:

1. Constructing effective PubMed search queries
2. Filtering and ranking research papers by relevance and quality
3. Identifying key findings from abstracts
4. Recognizing high-impact journals and influential studies
5. Understanding medical terminology and MeSH terms

When searching literature:
- Use appropriate medical terminology and synonyms
- Apply relevant filters (date range, article type, etc.)
- Prioritize systematic reviews and meta-analyses when available
- Consider study design quality (RCTs > observational studies)
- Note the publication venue and citation impact

Always provide:
- A summary of key papers found
- Main findings from the literature
- Quality assessment of the evidence
- Any notable gaps in the literature""",
            model="gemini-2.0-flash",
            tools=["pubmed_search", "web_search", "synthesize_literature"],
            temperature=0.3  # Lower temperature for more focused searches
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def search_literature(
        self,
        query: str,
        max_papers: int = 20,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search medical literature with intelligent query construction."""
        
        search_prompt = f"""Search for medical literature on: {query}

Maximum papers to retrieve: {max_papers}
{"Focus areas: " + ", ".join(focus_areas) if focus_areas else ""}

1. First, construct an optimized PubMed search query
2. Execute the search using the pubmed_search tool
3. Analyze the results and identify the most relevant papers
4. Provide a summary of key findings"""
        
        response = await self.think(search_prompt)
        
        return {
            "query": query,
            "analysis": response,
            "papers": self.get_from_memory("search_results") or []
        }


class ClinicalTrialsAgent(BaseAgent):
    """
    Agent specialized in clinical trials research and analysis.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="ClinicalTrialsAnalyst",
            role=AgentRole.ANALYST,
            description="Analyzes clinical trials and experimental treatments",
            system_prompt="""You are a Clinical Trials Analyst AI agent. Your expertise includes:

1. Searching ClinicalTrials.gov effectively
2. Understanding trial phases (Phase 1-4)
3. Analyzing trial designs and endpoints
4. Interpreting inclusion/exclusion criteria
5. Assessing trial status and timelines
6. Identifying promising experimental treatments

When analyzing trials:
- Focus on trial phase and current status
- Note primary and secondary endpoints
- Consider enrollment targets and actual enrollment
- Assess sponsor credibility (academic vs pharma)
- Look at geographic distribution of trial sites

Provide insights on:
- Current trial landscape for the condition/treatment
- Promising interventions in development
- Timeline to potential approvals
- Gaps in clinical research""",
            model="gemini-2.0-flash",
            tools=["clinical_trials_search"],
            temperature=0.4
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def analyze_trials(
        self,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        phase: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze clinical trials for a condition or intervention."""
        
        query_parts = []
        if condition:
            query_parts.append(f"Condition: {condition}")
        if intervention:
            query_parts.append(f"Intervention: {intervention}")
        if phase:
            query_parts.append(f"Phase: {', '.join(phase)}")
            
        analysis_prompt = f"""Analyze clinical trials for:
{chr(10).join(query_parts)}

1. Search for relevant clinical trials
2. Categorize by phase and status
3. Identify the most promising studies
4. Provide insights on the development pipeline"""
        
        response = await self.think(analysis_prompt)
        
        return {
            "condition": condition,
            "intervention": intervention,
            "analysis": response,
            "trials": self.get_from_memory("trial_results") or []
        }


class DrugInformationAgent(BaseAgent):
    """
    Agent specialized in drug and pharmaceutical information.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="DrugInfoSpecialist",
            role=AgentRole.SPECIALIST,
            description="Provides comprehensive drug and pharmaceutical information",
            system_prompt="""You are a Drug Information Specialist AI agent. Your expertise covers:

1. Drug mechanisms of action
2. Pharmacokinetics and pharmacodynamics
3. Drug-drug interactions
4. Adverse effects and safety profiles
5. FDA approval status and indications
6. Off-label uses and emerging applications
7. Biosimilars and generic alternatives

When researching drugs:
- Verify FDA approval status and indications
- Note black box warnings if any
- Identify significant drug interactions
- Consider patient population factors
- Reference authoritative sources (FDA labels, UpToDate)

Provide:
- Comprehensive drug profiles
- Safety considerations
- Comparison with alternatives
- Practical clinical considerations""",
            model="gemini-2.0-flash",
            tools=["drug_database", "pubmed_search", "web_search"],
            temperature=0.3
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def get_drug_info(
        self,
        drug_name: str,
        include_interactions: bool = True,
        include_alternatives: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive drug information."""
        
        info_prompt = f"""Provide comprehensive information about: {drug_name}

Include:
1. Basic drug information (class, mechanism)
2. Approved indications
3. {"Drug interactions" if include_interactions else ""}
4. Safety profile and warnings
5. {"Alternative treatments" if include_alternatives else ""}"""
        
        response = await self.think(info_prompt)
        
        return {
            "drug_name": drug_name,
            "information": response,
            "data": self.get_from_memory("drug_data") or {}
        }


class SynthesisAgent(BaseAgent):
    """
    Agent specialized in synthesizing research findings into coherent reports.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="ResearchSynthesizer",
            role=AgentRole.SYNTHESIZER,
            description="Synthesizes research findings into comprehensive reports",
            system_prompt="""You are a Research Synthesis AI agent. Your role is to:

1. Integrate findings from multiple sources
2. Identify consensus and contradictions
3. Assess quality and strength of evidence
4. Highlight knowledge gaps
5. Generate actionable insights
6. Create well-structured research reports

When synthesizing:
- Organize information logically
- Weight evidence by quality (RCTs > observational)
- Note level of consensus in the field
- Highlight areas of uncertainty
- Provide balanced conclusions

Output formats you can produce:
- Executive summaries
- Detailed research reports
- Evidence tables
- Gap analyses
- Recommendations""",
            model="gemini-2.0-flash",
            tools=["synthesize_literature"],
            reflection_enabled=True,
            temperature=0.5
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def synthesize(
        self,
        research_data: Dict[str, Any],
        output_format: str = "comprehensive_report"
    ) -> str:
        """Synthesize research data into a report."""
        
        synthesis_prompt = f"""Synthesize the following research data into a {output_format}:

RESEARCH DATA:
{json.dumps(research_data, indent=2, default=str)[:8000]}

Create a well-structured synthesis that:
1. Summarizes key findings
2. Identifies patterns and themes
3. Notes contradictions or gaps
4. Provides evidence-based conclusions
5. Offers recommendations if appropriate"""
        
        response = await self.think(synthesis_prompt)
        return response


class CriticAgent(BaseAgent):
    """
    Agent that reviews and critiques research findings for quality and completeness.
    """
    
    def __init__(self, llm_client: Any = None, tool_registry: Any = None):
        config = AgentConfig(
            name="ResearchCritic",
            role=AgentRole.CRITIC,
            description="Reviews and critiques research quality and completeness",
            system_prompt="""You are a Research Critic AI agent. Your role is to:

1. Evaluate research quality and methodology
2. Identify potential biases
3. Check for logical consistency
4. Verify claims against evidence
5. Suggest improvements and additional research
6. Ensure comprehensive coverage

When critiquing:
- Apply rigorous scientific standards
- Check for cherry-picking of evidence
- Identify unsupported conclusions
- Note limitations of cited studies
- Suggest ways to strengthen the research

Provide constructive feedback that helps improve the research quality.""",
            model="gemini-2.0-flash",
            reflection_enabled=True,
            temperature=0.4
        )
        super().__init__(config, llm_client, tool_registry)
    
    async def critique(
        self,
        research_output: str,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Critique research output."""
        
        critique_prompt = f"""Critically evaluate the following research output:

{research_output[:6000]}

{"Evaluation criteria: " + ", ".join(criteria) if criteria else ""}

Assess:
1. Quality of evidence cited
2. Logical consistency
3. Completeness of coverage
4. Potential biases
5. Accuracy of conclusions

Provide specific, actionable feedback."""
        
        response = await self.think(critique_prompt)
        
        return {
            "critique": response,
            "quality_score": self._extract_quality_score(response),
            "improvements_suggested": self._extract_improvements(response)
        }
    
    def _extract_quality_score(self, critique: str) -> Optional[float]:
        """Extract quality score from critique (if mentioned)."""
        # Simple extraction - would be more sophisticated in production
        import re
        score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', critique)
        if score_match:
            return float(score_match.group(1))
        return None
    
    def _extract_improvements(self, critique: str) -> List[str]:
        """Extract improvement suggestions from critique."""
        # Simple extraction - would be more sophisticated in production
        improvements = []
        lines = critique.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['should', 'could', 'recommend', 'suggest', 'improve']):
                improvements.append(line.strip())
        return improvements[:5]


# ============================================================================
# Agent Team / Multi-Agent System
# ============================================================================

class AgentTeam:
    """
    Manages a team of agents that work together on research tasks.
    Implements Agno-style multi-agent coordination.
    """
    
    def __init__(
        self,
        llm_client: Any = None,
        tool_registry: Any = None
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        
        # Initialize all agents
        self.coordinator = ResearchCoordinatorAgent(llm_client, tool_registry)
        self.literature_agent = LiteratureSearchAgent(llm_client, tool_registry)
        self.trials_agent = ClinicalTrialsAgent(llm_client, tool_registry)
        self.drug_agent = DrugInformationAgent(llm_client, tool_registry)
        self.synthesis_agent = SynthesisAgent(llm_client, tool_registry)
        self.critic_agent = CriticAgent(llm_client, tool_registry)
        
        self.agents = {
            "coordinator": self.coordinator,
            "literature": self.literature_agent,
            "trials": self.trials_agent,
            "drugs": self.drug_agent,
            "synthesis": self.synthesis_agent,
            "critic": self.critic_agent
        }
        
        self.execution_log: List[Dict[str, Any]] = []
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def reset_all(self) -> None:
        """Reset all agents."""
        for agent in self.agents.values():
            agent.reset()
        self.execution_log = []
    
    async def execute_research(
        self,
        query: str,
        include_critique: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a full research workflow with all agents.
        
        This implements the Agno multi-agent execution pattern.
        """
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Planning
        self._log("Starting research planning")
        plan = await self.coordinator.create_research_plan(query)
        results["stages"]["planning"] = plan
        
        # Stage 2: Execute subtasks based on plan
        subtasks = plan.get("subtasks", [])
        
        for task in subtasks:
            task_type = task.get("type", "")
            task_desc = task.get("description", "")
            
            self._log(f"Executing task: {task_type}")
            
            if task_type == "literature_search":
                lit_results = await self.literature_agent.search_literature(task_desc)
                results["stages"][f"literature_{task.get('id', '')}"] = lit_results
                
            elif task_type == "clinical_trial_search":
                trial_results = await self.trials_agent.analyze_trials(
                    condition=task.get("parameters", {}).get("condition"),
                    intervention=task.get("parameters", {}).get("intervention")
                )
                results["stages"][f"trials_{task.get('id', '')}"] = trial_results
                
            elif task_type == "drug_lookup":
                drug_results = await self.drug_agent.get_drug_info(
                    task.get("parameters", {}).get("drug_name", task_desc)
                )
                results["stages"][f"drug_{task.get('id', '')}"] = drug_results
        
        # Stage 3: Synthesis
        self._log("Synthesizing results")
        synthesis = await self.synthesis_agent.synthesize(results["stages"])
        results["synthesis"] = synthesis
        
        # Stage 4: Critique (optional)
        if include_critique:
            self._log("Applying critique")
            critique = await self.critic_agent.critique(synthesis)
            results["critique"] = critique
        
        results["execution_log"] = self.execution_log
        
        return results
    
    def _log(self, message: str) -> None:
        """Log execution step."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })


# ============================================================================
# Factory Functions
# ============================================================================

def create_agent_team(
    llm_client: Any = None,
    tool_registry: Any = None
) -> AgentTeam:
    """Create a fully configured agent team."""
    return AgentTeam(llm_client, tool_registry)


def create_single_agent(
    agent_type: str,
    llm_client: Any = None,
    tool_registry: Any = None
) -> BaseAgent:
    """Create a single agent of the specified type."""
    
    agent_classes = {
        "coordinator": ResearchCoordinatorAgent,
        "literature": LiteratureSearchAgent,
        "trials": ClinicalTrialsAgent,
        "drugs": DrugInformationAgent,
        "synthesis": SynthesisAgent,
        "critic": CriticAgent
    }
    
    agent_class = agent_classes.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(llm_client, tool_registry)
