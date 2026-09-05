"""
LangGraph Workflows Package.

Contains workflow definitions for research orchestration:
- Research state management
- Workflow nodes
- Conditional routing
- Streaming execution
"""

from .langgraph_workflow import (
    # State
    ResearchPhase,
    ResearchState,
    create_initial_state,
    
    # Nodes
    GraphNode,
    PlanningNode,
    LiteratureSearchNode,
    ClinicalTrialsNode,
    DrugAnalysisNode,
    SynthesisNode,
    CritiqueNode,
    RevisionNode,
    CompleteNode,
    
    # Routing functions
    route_after_planning,
    route_after_literature,
    route_after_trials,
    route_after_critique,
    should_continue,
    
    # Workflow
    ResearchWorkflowGraph,
    StreamingWorkflowRunner,
    
    # Factory functions
    create_research_workflow,
    create_streaming_runner
)

__all__ = [
    # State
    "ResearchPhase",
    "ResearchState",
    "create_initial_state",
    
    # Nodes
    "GraphNode",
    "PlanningNode",
    "LiteratureSearchNode",
    "ClinicalTrialsNode",
    "DrugAnalysisNode",
    "SynthesisNode",
    "CritiqueNode",
    "RevisionNode",
    "CompleteNode",
    
    # Routing functions
    "route_after_planning",
    "route_after_literature",
    "route_after_trials",
    "route_after_critique",
    "should_continue",
    
    # Workflow
    "ResearchWorkflowGraph",
    "StreamingWorkflowRunner",
    
    # Factory functions
    "create_research_workflow",
    "create_streaming_runner"
]
