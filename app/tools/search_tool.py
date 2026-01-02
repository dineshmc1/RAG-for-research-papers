import os
import requests
from langchain_core.tools import tool

@tool
def google_scholar_search(query: str):
    """
    Search Google Scholar via Serper API to find paper citations and impact.
    Requires SERPER_API_KEY environment variable.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY not set"}

    url = "https://google.serper.dev/scholar"
    payload = json.dumps({
        "q": query,
        "num": 5
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

import json
