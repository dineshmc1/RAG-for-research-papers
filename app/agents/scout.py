from app.agents.state import AgentState
from app.tools.arxiv_tool import search_arxiv_papers
from app.tools.search_tool import google_scholar_search
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

def get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4o-mini")

def scout_node(state: AgentState):
    """
    Citation Scout: Verifies and searches for citations.
    """
    plan = state["research_plan"]
    current_idx = state["current_step_index"]
    step = plan[current_idx]
    
    if step["assigned_agent"] != "Citation_Scout":
        return {}

    query = step["description"]
    
    # 1. Decide Tool
    # Simple logic: If verification -> Arxiv, if impact -> Scholar/Serper
    # For now, search Arxiv.
    
    results = search_arxiv_papers.invoke({"query": query})
    
    # 2. Analyze
    llm = get_llm()
    prompt = f"""Task: {query}
    
    Search Results:
    {results}
    
    Summarize the findings."""
    
    response = llm.invoke([SystemMessage(content="You are a Citation Scout."), HumanMessage(content=prompt)])
    
    step["status"] = "completed"
    step["result"] = response.content
    
    new_plan = [s for s in plan]
    new_plan[current_idx] = step
    
    return {"research_plan": new_plan, "current_step_index": current_idx + 1}
