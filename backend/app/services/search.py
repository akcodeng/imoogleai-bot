"""
Imoogle 5.0 Search Service
Web search using Tavily API with fallback to SearXNG.
"""

import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from app.config import settings


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 0.0


class SearchService:
    """
    Web search service with:
    1. Tavily API (primary)
    2. SearXNG (fallback)
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.http_client.aclose()
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
    ) -> List[SearchResult]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"
        
        Returns:
            List of SearchResult objects
        """
        # Try Tavily first
        if settings.TAVILY_API_KEY:
            try:
                return await self._tavily_search(query, max_results, search_depth)
            except Exception as e:
                print(f"[ImoogleAI] Tavily search failed: {e}")
        
        # Fallback to SearXNG
        if settings.SEARXNG_URL:
            try:
                return await self._searxng_search(query, max_results)
            except Exception as e:
                print(f"[ImoogleAI] SearXNG search failed: {e}")
        
        return []
    
    async def _tavily_search(
        self,
        query: str,
        max_results: int,
        search_depth: str,
    ) -> List[SearchResult]:
        """Search using Tavily API."""
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False,
        }
        
        response = await self.http_client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                score=item.get("score", 0.0),
            ))
        
        return results
    
    async def _searxng_search(
        self,
        query: str,
        max_results: int,
    ) -> List[SearchResult]:
        """Search using SearXNG instance."""
        url = f"{settings.SEARXNG_URL}/search"
        
        params = {
            "q": query,
            "format": "json",
            "engines": "google,bing,duckduckgo",
        }
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("results", [])[:max_results]:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                score=item.get("score", 0.0),
            ))
        
        return results
    
    def format_results(
        self,
        results: List[SearchResult],
        use_pidgin: bool = False,
    ) -> str:
        """Format search results for display."""
        if not results:
            if use_pidgin:
                return "Omo, I no fit find anything for wetin you search o. Try search something else."
            return "I couldn't find any results for that search. Try rephrasing your query."
        
        if use_pidgin:
            formatted = "See wetin I find for you:\n\n"
        else:
            formatted = "Here's what I found:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. [{result.title}]({result.url})**\n"
            formatted += f"{result.snippet[:200]}...\n\n"
        
        return formatted


# Singleton instance
search_service = SearchService()
