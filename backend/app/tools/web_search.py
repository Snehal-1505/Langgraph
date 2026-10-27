import logging
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from app.config import settings
from app.tools.source_validator import is_safe_url

logger = logging.getLogger(__name__)


class WebSearchProvider:
    """Abstract interface and implementation for web search providers."""

    def __init__(self, provider: str = settings.SEARCH_PROVIDER, tavily_api_key: Optional[str] = settings.TAVILY_API_KEY):
        self.provider = provider
        self.tavily_api_key = tavily_api_key

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Execute a search query using the configured provider.
        Returns a list of dicts: [{"title": ..., "url": ..., "snippet": ..., "domain": ...}]
        """
        if not query or not query.strip():
            return []

        if self.provider == "mock":
            return self._mock_search(query, max_results)

        if self.provider == "tavily" and self.tavily_api_key:
            try:
                return await self._tavily_search(query, max_results)
            except Exception as e:
                logger.warning(f"Tavily search failed: {e}. Falling back to DuckDuckGo.")
                return await self._duckduckgo_search(query, max_results)

        # Default to DuckDuckGo
        return await self._duckduckgo_search(query, max_results)

    async def _duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform search using DuckDuckGo."""
        results = []
        try:
            from duckduckgo_search import DDGS
            # Run blocking ddgs search in thread
            def _run_ddg():
                ddgs = DDGS(timeout=settings.REQUEST_TIMEOUT_SECONDS)
                return list(ddgs.text(query, max_results=max_results))

            raw_results = await asyncio.to_thread(_run_ddg)
            for item in raw_results:
                url = item.get("href") or item.get("url")
                if not url:
                    continue
                safe, _ = is_safe_url(url)
                if not safe:
                    continue

                domain = urlparse(url).netloc
                results.append({
                    "title": item.get("title", ""),
                    "url": url,
                    "snippet": item.get("body", ""),
                    "domain": domain
                })
        except Exception as e:
            logger.error(f"DuckDuckGo search error for query '{query}': {str(e)}")
            # Do not invent fake results; return empty list with logged error

        return results

    async def _tavily_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform search using Tavily API."""
        import httpx
        results = []
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "include_domains": [],
            "exclude_domains": []
        }
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", []):
                    u = item.get("url")
                    if not u:
                        continue
                    safe, _ = is_safe_url(u)
                    if not safe:
                        continue
                    results.append({
                        "title": item.get("title", ""),
                        "url": u,
                        "snippet": item.get("content", ""),
                        "domain": urlparse(u).netloc
                    })
            else:
                logger.error(f"Tavily returned error status {resp.status_code}: {resp.text}")
        return results

    def _mock_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Deterministic mock results for testing without external networks."""
        return [
            {
                "title": f"Empirical Study on {query[:30]}",
                "url": f"https://example.org/research/{abs(hash(query)) % 10000}",
                "snippet": f"Key verified findings regarding {query}. This analysis outlines trends, productivity metrics, and limitations observed in field evaluations.",
                "domain": "example.org"
            },
            {
                "title": f"Industry Report: Trends in {query[:25]}",
                "url": f"https://example.edu/papers/{abs(hash(query + '2')) % 10000}",
                "snippet": f"Detailed academic assessment of {query}. Includes comparative risk analysis and institutional impact metrics.",
                "domain": "example.edu"
            }
        ][:max_results]
