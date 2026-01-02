# Agentic Research Lab - Verification & Run Guide

## Prerequisites
- Python 3.10+
- OpenAI API Key (or compatible)
- Serper API Key (for citation verification)

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
1. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```
2. Open your browser at `http://localhost:8501`.

## Usage
1. **Sidebar**: Enter your OpenAI and Serper API Keys.
2. **Upload**: Upload a research paper PDF.
3. **Chat**: Ask questions like:
   - "Summarize the methodology."
   - "Verify the citations in the results section."
   - "Create a flowchart of the proposed architecture."

## Verification Checklist
- [ ] **PDF Upload**: Ensure "File processed" message appears.
- [ ] **Plan Generation**: Ask a complex question and check "Research Plan" in the right column.
- [ ] **Agents**: Verify that specific agents (Analyst, Scout, Visualizer) are assigned tasks in the plan.
- [ ] **Output**: Check that the final answer cites sections or external papers.
- [ ] **Visualization**: Check that Mermaid diagrams are rendered.

## Notes
- The system uses `chromadb` for local vector storage.
- Models are configured to use `gpt-4o-mini` by default for stability, but can be swapped in `app/agents/*.py`.
