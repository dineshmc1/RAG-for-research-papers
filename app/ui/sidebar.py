import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        st.title("🤖 Agentic Research Lab")
        st.markdown("---")
        
        st.subheader("Configuration")
        
        openai_key = st.text_input("OpenAI API Key", type="password")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
            
        serper_key = st.text_input("Serper API Key", type="password")
        if serper_key:
            os.environ["SERPER_API_KEY"] = serper_key

        st.markdown("### Settings")
        mode = st.radio("Mode", ["Research Mode", "Quick Chat"])
        st.caption("Plan-and-Execute Agent System")
        
        st.markdown("---")
        st.info("Upload a PDF to begin.")
