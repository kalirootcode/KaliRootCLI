"""
Web Search Module for KaliRootCLI
Real-time internet search using DuckDuckGo for enriched AI responses.

Features:
- General web search
- Security-focused searches
- News and CVE lookups
- No API key required
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import duckduckgo_search
try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    DDGS = None
    SEARCH_AVAILABLE = False
    logger.warning("duckduckgo-search not installed. Web search disabled.")


@dataclass
class SearchResult:
    """Structured search result."""
    title: str
    body: str
    url: str
    source: str = ""
    date: str = ""


class WebSearchAgent:
    """
    Professional web search agent for enriching AI responses with real-time data.
    
    Uses DuckDuckGo for privacy-respecting searches without requiring API keys.
    """
    
    def __init__(self, max_results: int = 5, timeout: int = 10):
        """
        Initialize the web search agent.
        
        Args:
            max_results: Maximum number of results to return per search
            timeout: Request timeout in seconds
        """
        self.max_results = max_results
        self.timeout = timeout
        self._ddgs: Optional[DDGS] = None
        
    @property
    def ddgs(self) -> Optional[DDGS]:
        """Lazy initialization of DDGS client."""
        if not SEARCH_AVAILABLE:
            return None
        if self._ddgs is None:
            self._ddgs = DDGS(timeout=self.timeout)
        return self._ddgs
    
    @property
    def is_available(self) -> bool:
        """Check if web search is available."""
        return SEARCH_AVAILABLE and self.ddgs is not None
    
    def search(
        self, 
        query: str, 
        region: str = "wt-wt",
        safesearch: str = "moderate"
    ) -> List[SearchResult]:
        """
        Search the web for relevant information.
        
        Args:
            query: Search query
            region: Region code (wt-wt for worldwide)
            safesearch: Filter level (off, moderate, strict)
            
        Returns:
            List of SearchResult objects
        """
        if not self.is_available:
            logger.warning("Web search not available")
            return []
            
        try:
            results = list(self.ddgs.text(
                query, 
                region=region, 
                max_results=self.max_results,
                safesearch=safesearch
            ))
            
            return [
                SearchResult(
                    title=r.get("title", ""),
                    body=r.get("body", ""),
                    url=r.get("href", ""),
                    source=self._extract_domain(r.get("href", ""))
                )
                for r in results
            ]
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def search_news(
        self, 
        query: str, 
        timelimit: str = "d"
    ) -> List[SearchResult]:
        """
        Search for recent news articles.
        
        Args:
            query: News search query
            timelimit: Time filter (d=day, w=week, m=month)
            
        Returns:
            List of news SearchResult objects
        """
        if not self.is_available:
            return []
            
        try:
            results = list(self.ddgs.news(
                query,
                timelimit=timelimit,
                max_results=self.max_results
            ))
            
            return [
                SearchResult(
                    title=r.get("title", ""),
                    body=r.get("body", ""),
                    url=r.get("url", ""),
                    source=r.get("source", ""),
                    date=r.get("date", "")
                )
                for r in results
            ]
        except Exception as e:
            logger.error(f"News search error: {e}")
            return []
    
    def search_security(self, query: str) -> str:
        """
        Specialized search for cybersecurity topics.
        Returns formatted context string for AI prompts.
        
        Args:
            query: Security-related search query
            
        Returns:
            Formatted string with search results for AI context
        """
        # Enhance query for security context
        security_query = f"cybersecurity {query}"
        results = self.search(security_query)
        
        if not results:
            return ""
        
        context = "\n[📡 DATOS WEB EN TIEMPO REAL]\n"
        context += f"Búsqueda: '{query}' | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        context += "─" * 50 + "\n"
        
        for i, r in enumerate(results[:3], 1):
            context += f"\n{i}. **{r.title}**\n"
            context += f"   {r.body[:250]}{'...' if len(r.body) > 250 else ''}\n"
            context += f"   🔗 {r.source}\n"
        
        context += "\n" + "─" * 50 + "\n"
        return context
    
    def search_cve(self, cve_id: str = None, keyword: str = None) -> str:
        """
        Search for CVE information.
        
        Args:
            cve_id: Specific CVE ID (e.g., CVE-2024-1234)
            keyword: Keyword to search CVEs for
            
        Returns:
            Formatted CVE information for AI context
        """
        if cve_id:
            query = f"{cve_id} vulnerability details exploit"
        elif keyword:
            query = f"CVE {keyword} vulnerability 2024"
        else:
            return ""
        
        results = self.search(query)
        
        if not results:
            return ""
        
        context = "\n[🛡️ INFORMACIÓN CVE]\n"
        context += f"Consulta: '{cve_id or keyword}'\n"
        context += "─" * 50 + "\n"
        
        for r in results[:3]:
            context += f"\n• {r.title}\n"
            context += f"  {r.body[:200]}...\n"
            context += f"  Fuente: {r.source}\n"
        
        return context
    
    def search_tool(self, tool_name: str) -> str:
        """
        Search for security tool documentation and usage.
        
        Args:
            tool_name: Name of the security tool
            
        Returns:
            Formatted tool information for AI context
        """
        query = f"{tool_name} security tool usage tutorial kali"
        results = self.search(query)
        
        if not results:
            return ""
        
        context = f"\n[🔧 HERRAMIENTA: {tool_name.upper()}]\n"
        context += "─" * 50 + "\n"
        
        for r in results[:2]:
            context += f"\n• {r.title}\n"
            context += f"  {r.body[:200]}...\n"
        
        return context
    
    def get_latest_threats(self) -> str:
        """
        Get information about latest cybersecurity threats.
        
        Returns:
            Formatted threat intelligence for AI context
        """
        news = self.search_news("cybersecurity threat attack vulnerability", timelimit="w")
        
        if not news:
            return ""
        
        context = "\n[⚠️ AMENAZAS RECIENTES]\n"
        context += f"Actualizado: {datetime.now().strftime('%Y-%m-%d')}\n"
        context += "─" * 50 + "\n"
        
        for n in news[:3]:
            context += f"\n📰 {n.title}\n"
            if n.date:
                context += f"   Fecha: {n.date}\n"
            context += f"   {n.body[:150]}...\n"
        
        return context
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return url[:50] if url else ""
    
    def format_results_for_display(self, results: List[SearchResult]) -> str:
        """
        Format search results for terminal display.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Rich-formatted string for console output
        """
        if not results:
            return "[yellow]No se encontraron resultados.[/yellow]"
        
        output = ""
        for i, r in enumerate(results, 1):
            output += f"\n[bold cyan]{i}.[/bold cyan] [bold]{r.title}[/bold]\n"
            output += f"   [dim]{r.body[:200]}{'...' if len(r.body) > 200 else ''}[/dim]\n"
            output += f"   [blue underline]{r.url}[/blue underline]\n"
        
        return output


# Global instance
web_search = WebSearchAgent()

# Convenience functions
def search(query: str) -> List[SearchResult]:
    """Quick search function."""
    return web_search.search(query)

def search_security(query: str) -> str:
    """Quick security search for AI context."""
    return web_search.search_security(query)

def is_search_available() -> bool:
    """Check if search is available."""
    return web_search.is_available
