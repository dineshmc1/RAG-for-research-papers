from app.agents.state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4o-mini")

def visualizer_node(state: AgentState):
    """
    Visual Specialist: Generates Mermaid diagrams.
    """
    plan = state["research_plan"]
    current_idx = state["current_step_index"]
    step = plan[current_idx]
    
    if step["assigned_agent"] != "Visual_Specialist":
        return {}

    query = step["description"]
    
    # Context? Might need context from previous steps or PDF.
    # We will look at previous steps results for context if needed, or PDF RAG.
    # For simplicity, assume the query describes what to visualize based on general knowledge or explicit context provided in the query itself.
    
    llm = get_llm()
    prompt = f"""Task: {query}
    
    Generate a Mermaid.js diagram code block.
    Format:
    ```mermaid
    ...
    ```
    Only output the code."""
    
    response = llm.invoke([SystemMessage(content="You are a Visual Specialist. Create valid Mermaid diagrams."), HumanMessage(content=prompt)])
    
    content = response.content
    diagram = ""
    if "```mermaid" in content:
        diagram = content.split("```mermaid")[1].split("```")[0].strip()
    elif "```" in content:
        diagram = content.split("```")[1].split("```")[0].strip()
    else:
        diagram = content # Hope it's just code
        
    step["status"] = "completed"
    step["result"] = f"Generated Diagram:\n```mermaid\n{diagram}\n```"
    
    new_plan = [s for s in plan]
    new_plan[current_idx] = step
    
    # Store diagram in state list
    current_diagrams = state.get("diagrams", []) or []
    current_diagrams.append(diagram)
    
    return {"research_plan": new_plan, "current_step_index": current_idx + 1, "diagrams": current_diagrams}
