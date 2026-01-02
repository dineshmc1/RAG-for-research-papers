from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ResearchPlanStep(TypedDict):
    id: int
    description: str
    assigned_agent: str
    status: str # "pending", "in_progress", "completed"
    result: str | None

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    research_plan: List[ResearchPlanStep]
    documents: List[Dict[str, Any]] # Chunk content, metadata
    verified_citations: List[Dict[str, Any]]
    diagrams: List[str] # Mermaid code or JSON
    current_step_index: int
    final_answer: str
