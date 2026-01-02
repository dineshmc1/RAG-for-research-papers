import arxiv
from langchain_core.tools import tool

@tool
def search_arxiv_papers(query: str, max_results: int = 5):
    """
    Search for papers on Arxiv.
    Returns a list of papers with title, summary, authors, and pdf_url.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for result in client.results(search):
        results.append({
            "title": result.title,
            "summary": result.summary,
            "authors": [a.name for a in result.authors],
            "pdf_url": result.pdf_url,
            "published": str(result.published)
        })
    return results

@tool
def get_arxiv_paper_details(paper_id: str):
    """
    Get details for a specific Arxiv paper by ID.
    """
    client = arxiv.Client()
    search = arxiv.Search(id_list=[paper_id])
    results = list(client.results(search))
    
    if not results:
        return {"error": "Paper not found"}
        
    result = results[0]
    return {
        "title": result.title,
        "summary": result.summary,
        "authors": [a.name for a in result.authors],
        "pdf_url": result.pdf_url,
        "published": str(result.published)
    }
