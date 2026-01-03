import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


import streamlit as st
import os
import sys
import tempfile

# Add project root to sys.path to allow 'from app...' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ui.sidebar import render_sidebar
from app.ui.chat import render_chat_history, render_plan_status, render_mermaid
from app.agents.graph import build_graph
from app.rag.ingestion import ingest_pdf
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Agentic Research Lab", layout="wide")

def main():
    render_sidebar()
    
    st.title("🧪 Agentic Research Lab")
    st.caption("Advanced Multi-Agent System for Research Paper Analysis")

    # Session State Init
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()
    if "plan" not in st.session_state:
        st.session_state.plan = []
    if "diagrams" not in st.session_state:
        st.session_state.diagrams = []

    # File Upload
    uploaded_file = st.file_uploader("Upload Research Paper (PDF)", type="pdf")
    
    if uploaded_file:
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            with st.spinner("Analyzing PDF structure and creating vector embeddings..."):
                # Save to temp
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    temp_path = tmp.name
                
                success, msg = ingest_pdf(temp_path)
                if success:
                    st.success(f"File processed: {msg}")
                    st.session_state.current_file = uploaded_file.name
                else:
                    st.error(f"Error: {msg}")

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Chat & Research")
        render_chat_history(st.session_state.messages)
        
        user_input = st.chat_input("Ask a question about the paper...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append(HumanMessage(content=user_input))
            
            # Prepare State
            initial_state = {
                "messages": st.session_state.messages,
                "user_query": user_input,
                "research_plan": st.session_state.plan,
                "current_step_index": len([s for s in st.session_state.plan if s["status"]=="completed"]), # Resume or start
                "documents": [],
                "verified_citations": [],
                "diagrams": st.session_state.diagrams
            }
            
            # Reset plan if it's a new discrete query? 
            # For this simple "Lead Researcher" flow, if we want a fresh plan for a fresh query, we might want to clear old plan.
            # But maybe we want context. Let's assume new query = new plan for now to keep it clean.
            if len(st.session_state.messages) > 2: # Heuristic: if verifying or follow up, maybe keep? 
                # Simplification: Always refresh plan for new root query
                initial_state["research_plan"] = []
                initial_state["current_step_index"] = 0
            
            with st.spinner("Agents are working..."):
                # Stream the graph updates
                # We need to capture the final state
                final_state = None
                for event in st.session_state.graph.stream(initial_state):
                    # We can log events or update UI incrementally here if we want detailed "Thought" process
                    for key, value in event.items():
                        # Update session state plan live?
                        if "research_plan" in value:
                            st.session_state.plan = value["research_plan"]
                            # Force rerun to show plan update?
                            # st.rerun() # effectively reloads, might be jittery. Better to just wait for final.
                            pass
                        if "diagrams" in value:
                            st.session_state.diagrams = value["diagrams"]
                            
                    # Last event is usually the final state
                    final_state = value # This might be partial, need to be careful with stream
            
            # After loop, final_state might be the last node output. 
            # We want the "accumulated" state logic handling or just rely on what we stored.
            # LangGraph stream output depends on config.
            
            # Let's run invoke() instead for simplicity if streaming is complex to render right now, 
            # but stream is better for UX.
            # For this boilerplate, let's use invoke() to ensure we get the final complete state easily.
            final_state = st.session_state.graph.invoke(initial_state)
            
            if "final_answer" in final_state and final_state["final_answer"]:
                st.session_state.messages.append(AIMessage(content=final_state["final_answer"]))
            
            st.session_state.plan = final_state.get("research_plan", [])
            st.session_state.diagrams = final_state.get("diagrams", [])
            
            st.rerun()

    with col2:
        st.subheader("Live Agent Monitor")
        render_plan_status(st.session_state.plan)
        
        if st.session_state.diagrams:
            st.subheader("Visualizations")
            for diag in st.session_state.diagrams:
                render_mermaid(diag)

if __name__ == "__main__":
    main()
