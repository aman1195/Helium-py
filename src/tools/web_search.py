import os
import httpx
from typing import Dict, List, Optional
from ..core.config import Config
from ..core.utils import logger

class WebSearchTool:
    """A tool for performing web searches."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.SEARCH_API_KEY
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            logger.warning("No search API key provided. Web search functionality will be limited.")
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Perform a web search and return results.
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        if not self.api_key:
            return [{
                "title": "Error: No API Key",
                "link": "",
                "snippet": "Search API key not configured. Please set SEARCH_API_KEY in your environment variables."
            }]
            
        params = {
            "q": query,
            "key": self.api_key,
            "cx": "YOUR_SEARCH_ENGINE_ID",  # You'll need to set this up in Google Programmable Search
            "num": min(num_results, 10)  # Google Custom Search API max is 10
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                return [{
                    "title": item.get("title", "No title"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "No description available.")
                } for item in data.get("items", [])]
                
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return [{
                "title": "Search Error",
                "link": "",
                "snippet": f"An error occurred while performing the search: {str(e)}"
            }]
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """Fetch the content of a web page.
        
        Args:
            url: The URL of the page to fetch
            
        Returns:
            The page content as text, or None if an error occurs
        """
        try:
            headers = {
                "User-Agent": "HeliumAI/1.0 (https://example.com/helium-ai; contact@example.com)"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, follow_redirects=True, timeout=10.0)
                response.raise_for_status()
                return response.text
                
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {str(e)}")
            return None
