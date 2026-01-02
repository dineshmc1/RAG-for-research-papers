from app.agents.state import AgentState
from app.rag.retrieval import retrieve_context
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4o-mini")

def analyst_node(state: AgentState):
    """
    PDF Analyst: Executes RAG tasks.
    """
    plan = state["research_plan"]
    current_idx = state["current_step_index"]
    step = plan[current_idx]
    
    if step["assigned_agent"] != "PDF_Analyst":
        return {} # Should not happen if routing is correct
        
    query = step["description"]
    
    # 1. Retrieve
    # Extract keywords or use full query? Using full query for now.
    results = retrieve_context(query)
    context_str = "\n".join([f"[Page {r['metadata']['page']}] {r['content'][:200]}..." for r in results])
    full_context_str = "\n".join([f"Content: {r['content']}\nMetadata: {r['metadata']}" for r in results])

    # 2. Analyze
    llm = get_llm()
    prompt = f"""Task: {query}
    
    Context from PDF:
    {full_context_str}
    
    Provide the answer to the task based *strictly* on the context."""
    
    response = llm.invoke([SystemMessage(content="You are a PDF Analyst. Be precise."), HumanMessage(content=prompt)])
    
    # Update Plan Step
    step["status"] = "completed"
    step["result"] = response.content
    
    # Update State
    # Note: In LangGraph, we return the DIFF.
    # However for a list of dicts (plan), we might need to replace the whole list or be careful.
    # Here we are modifying the object reference obtained from state. 
    # To be safe in functional style, we should reconstruct.
    
    new_plan = [s for s in plan]
    new_plan[current_idx] = step
    
    return {"research_plan": new_plan, "current_step_index": current_idx + 1}
