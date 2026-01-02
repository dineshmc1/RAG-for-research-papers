from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agents.state import AgentState, ResearchPlanStep
import json

# Placeholder for DeepSeek/Qwen model config
# Users should set OPENAI_API_BASE for local models or use standard OpenAI
LLM_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" # Conceptual name, might need adjustment based on provider

def get_llm():
    # Fallback/Config wrapper
    return ChatOpenAI(temperature=0, model="gpt-4o-mini") # Using a reliable default for the boilerplate, user can swap.

def researcher_node(state: AgentState):
    """
    Lead Researcher: Analyzes query and creates a plan.
    """
    query = state["user_query"]
    messages = state["messages"]
    
    # If a plan exists, this might be a refinement or final synthesis step? 
    # For this simple Plan-Execute flow, we assume:
    # 1. State init -> Researcher (Create Plan) -> Route to Agents
    # 2. Agents return -> Researcher (Synthesize) -> End
    
    if not state.get("research_plan"):
        # CREATE PLAN
        llm = get_llm()
        system_msg = """You are the Lead Researcher in an advanced agentic lab.
        Your goal is to breakdown the user's research query into steps.
        Available Agents:
        - PDF_Analyst: For extracting information from the uploaded paper.
        - Citation_Scout: For searching external papers and verifying citations.
        - Visual_Specialist: For creating diagrams (Mermaid) or Knowledge Graphs.
        
        Output a JSON list of steps. Each step must have:
        - "description": What to do.
        - "assigned_agent": One of [PDF_Analyst, Citation_Scout, Visual_Specialist].
        """
        
        prompt = f"User Query: {query}\n\nCreate a research plan."
        response = llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=prompt)])
        
        # Simple JSON parsing (robustness needed in prod)
        try:
            content = response.content.strip()
            # Handle markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            steps_data = json.loads(content)
            # Add IDs
            plan = []
            for i, s in enumerate(steps_data):
                plan.append({
                    "id": i+1,
                    "description": s["description"],
                    "assigned_agent": s["assigned_agent"],
                    "status": "pending",
                    "result": None
                })
            
            return {"research_plan": plan, "current_step_index": 0, "messages": [AIMessage(content="I have created a research plan.")]}
        except Exception as e:
            return {"messages": [AIMessage(content=f"Error creating plan: {e}")]}

    else:
        # PLAN EXECUTION / SYNTHESIS
        # Check if all steps are done?
        plan = state["research_plan"]
        if all(s["status"] == "completed" for s in plan):
            # Synthesize final answer
            llm = get_llm()
            context = "\n".join([f"Step {s['id']} ({s['assigned_agent']}): {s['result']}" for s in plan])
            
            prompt = f"""User Query: {query}
            
            Research Results:
            {context}
            
            Synthesize a comprehensive answer. Cite the papers and sections used."""
            
            response = llm.invoke([SystemMessage(content="You are a Lead Researcher. Synthesize the findings."), HumanMessage(content=prompt)])
            return {"final_answer": response.content}
        
        return {} # Continue graph execution
