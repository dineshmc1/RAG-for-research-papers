from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.researcher import researcher_node
from app.agents.analyst import analyst_node
from app.agents.scout import scout_node
from app.agents.visualizer import visualizer_node

def route_manager(state: AgentState):
    """
    Determines the next step based on the research plan status.
    """
    plan = state.get("research_plan")
    
    # If no plan yet, or we just finished synthesis (final_answer present)
    if not plan or state.get("final_answer"):
        return END

    # Find next pending step
    for step in plan:
        if step["status"] == "pending":
            return step["assigned_agent"]
            
    # If all completed, go back to researcher for synthesis
    return "Lead_Researcher"

def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("Lead_Researcher", researcher_node)
    workflow.add_node("PDF_Analyst", analyst_node)
    workflow.add_node("Citation_Scout", scout_node)
    workflow.add_node("Visual_Specialist", visualizer_node)
    
    # Set Entry
    workflow.set_entry_point("Lead_Researcher")
    
    # Edges from Agents -> Router calculation
    # We want to check the plan after each agent or after researcher creates plan.
    
    # Researcher -> Router
    workflow.add_conditional_edges(
        "Lead_Researcher",
        route_manager,
        {
            "PDF_Analyst": "PDF_Analyst",
            "Citation_Scout": "Citation_Scout",
            "Visual_Specialist": "Visual_Specialist",
            "Lead_Researcher": "Lead_Researcher", # Loop back for synthesis
            END: END
        }
    )
    
    # Agents -> Router check (which is effectively just checking plan again)
    # We can reuse the conditional edge logic, but typically we point to a router node or use conditional edges on all.
    
    # Simply point agents back to "Lead_Researcher" creates a loop through manager.
    # But optimal P&E often bypasses manager for execution.
    # Let's add a conditional edge capability to agents to forward to next agent directly or back to manager.
    
    for agent in ["PDF_Analyst", "Citation_Scout", "Visual_Specialist"]:
        workflow.add_conditional_edges(
            agent,
            route_manager,
             {
                "PDF_Analyst": "PDF_Analyst",
                "Citation_Scout": "Citation_Scout",
                "Visual_Specialist": "Visual_Specialist",
                "Lead_Researcher": "Lead_Researcher",
                END: END
            }
        )
        
    return workflow.compile()
