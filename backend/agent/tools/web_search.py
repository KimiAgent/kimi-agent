"""
Web Search Tool — uses DuckDuckGo by default (free, no key required).
Falls back to SerpAPI when SERPAPI_KEY is set in environment.
"""

import os
from typing import List, Dict, Any


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web and return a list of results.

    Returns:
        List of dicts with keys: title, url, snippet
    """
    serpapi_key = os.getenv("SERPAPI_KEY", "")

    if serpapi_key:
        return _serpapi_search(query, max_results, serpapi_key)
    return _duckduckgo_search(query, max_results)


def _duckduckgo_search(query: str, max_results: int) -> List[Dict[str, str]]:
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return results
    except Exception as e:
        return [{"title": "Search error", "url": "", "snippet": str(e)}]


def _serpapi_search(query: str, max_results: int, api_key: str) -> List[Dict[str, str]]:
    try:
        from serpapi import GoogleSearch

        search = GoogleSearch({"q": query, "api_key": api_key, "num": max_results})
        data = search.get_dict()
        results = []
        for r in data.get("organic_results", [])[:max_results]:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": r.get("snippet", ""),
            })
        return results
    except Exception as e:
        return [{"title": "Search error", "url": "", "snippet": str(e)}]


def format_search_results(results: List[Dict[str, str]]) -> str:
    """Format results into a string to inject into the agent prompt."""
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}")
        lines.append(f"    URL: {r['url']}")
        lines.append(f"    {r['snippet']}")
        lines.append("")
    return "\n".join(lines)
