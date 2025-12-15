"""
RAG Engine for KaliRoot CLI
Retrieval-Augmented Generation system to provide grounded vulnerability data.
"""

import re
import logging
from typing import List, Dict, Optional
from .tools.cve_lookup import search_cve

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    RAG Knowledge Base.
    Extracts entities (software versions) and retrieves CVEs.
    """
    
    def __init__(self):
        # Regex patterns to catch common service banners
        # e.g., "Apache 2.4.49", "OpenSSH 7.2p2", "nginx 1.18.0"
        self.version_pattern = re.compile(
            r'([a-zA-Z0-9_\-]+)\s+([0-9]+\.[0-9]+[a-zA-Z0-9_\.\-]*)', 
            re.IGNORECASE
        )
        
        # Ignored non-software terms to reduce noise
        self.ignore_list = {
            "version", "port", "tcp", "udp", "addr", "host", "scanning", 
            "syn", "stealth", "service", "start", "report", "done", "http"
        }

    def _extract_softwares(self, text: str) -> List[str]:
        """Extract potential software strings from text."""
        matches = self.version_pattern.findall(text)
        candidates = []
        
        for name, version in matches:
            if name.lower() not in self.ignore_list and len(name) > 2:
                candidates.append(f"{name} {version}")
                
        return list(set(candidates)) # Remove duplicates

    def get_context(self, user_query: str) -> str:
        """
        Build RAG context string for AI prompt.
        """
        entities = self._extract_softwares(user_query)
        if not entities:
            return ""
        
        context_parts = []
        
        for entity in entities:
            # Retrieve CVEs (this uses our cached lookup)
            logger.info(f"RAG Retrieval for: {entity}")
            cves = search_cve(entity, limit=2)
            
            if cves and "error" not in cves[0]:
                top_cve = cves[0]
                context_parts.append(
                    f"- {entity}: Found {top_cve.get('id')} ({top_cve.get('severity')}). "
                    f"Desc: {top_cve.get('description')[:100]}..."
                )
                
        if not context_parts:
            return ""
            
        header = "\n[VERIFIED VULNERABILITIES - RAG MEMORY]\n"
        return header + "\n".join(context_parts) + "\n"
