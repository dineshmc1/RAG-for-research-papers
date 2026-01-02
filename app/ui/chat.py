import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, HumanMessage

def render_chat_history(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)

def render_plan_status(plan):
    if not plan:
        return
        
    st.subheader("📋 Research Plan")
    
    # Create a DataFrame-like view or custom HTML
    for step in plan:
        status_icon = "⏳"
        if step["status"] == "completed":
            status_icon = "✅"
        elif step["status"] == "in_progress":
            status_icon = "🔄"
            
        with st.expander(f"{status_icon} Step {step['id']}: {step['assigned_agent']}"):
            st.write(f"**Task:** {step['description']}")
            if step["result"]:
                st.info(f"**Result:** {step['result']}")

def render_mermaid(code: str):
    """
    Render Mermaid diagram using simple HTML injection or specific component.
    Using HTML injection for simplicity in this boilerplate.
    """
    import base64
    
    # Clean code
    code = code.replace("```mermaid", "").replace("```", "").strip()
    
    mermaid_html = f"""
        <div class="mermaid">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    """
    components.html(mermaid_html, height=400, scrolling=True)
