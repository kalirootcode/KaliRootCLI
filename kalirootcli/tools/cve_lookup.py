"""
CVE Lookup Tool - Premium Feature
Search CVE database via NIST NVD API.
"""

import requests
from typing import Dict, List, Optional

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


import json
import os
import time
from datetime import datetime

# Local cache file
CACHE_FILE = os.path.join(os.path.dirname(__file__), "cve_cache.json")
CACHE_EXPIRY_DAYS = 30

def _load_cache() -> Dict:
    """Load local CVE cache."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(cache: Dict) -> None:
    """Save to local CVE cache."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def search_cve(keyword: str, limit: int = 5) -> List[Dict]:
    """
    Search CVE database by keyword (Cached).
    Returns list of CVEs with id, description, severity.
    """
    cache = _load_cache()
    
    # Check cache first
    # Simple cache logic: key = keyword
    if keyword in cache:
        entry = cache[keyword]
        # Check expiry (optional, but good practice)
        saved_at = entry.get("timestamp", 0)
        if time.time() - saved_at < (CACHE_EXPIRY_DAYS * 86400):
            return entry.get("results", [])
    
    try:
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": limit
        }
        
        response = requests.get(NVD_API, params=params, timeout=15)
        
        if response.status_code != 200:
            return cache.get(keyword, {}).get("results", []) # Return stale cache if API fails
        
        try:
            data = response.json()
        except ValueError:
            # API returned non-JSON (HTML error page, etc.)
            return cache.get(keyword, {}).get("results", [])
        vulnerabilities = data.get("vulnerabilities", [])
        
        results = []
        for vuln in vulnerabilities:
            cve = vuln.get("cve", {})
            cve_id = cve.get("id", "N/A")
            
            # Get description
            descriptions = cve.get("descriptions", [])
            desc = next((d["value"] for d in descriptions if d["lang"] == "en"), "No description")
            
            # Get severity
            metrics = cve.get("metrics", {})
            cvss = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", []))
            severity = "UNKNOWN"
            score = "N/A"
            
            if cvss:
                cvss_data = cvss[0].get("cvssData", {})
                severity = cvss_data.get("baseSeverity", "UNKNOWN")
                score = cvss_data.get("baseScore", "N/A")
            
            results.append({
                "id": cve_id,
                "description": desc[:200] + "..." if len(desc) > 200 else desc,
                "severity": severity,
                "score": score
            })
        
        # Save to cache
        cache[keyword] = {
            "timestamp": time.time(),
            "results": results
        }
        _save_cache(cache)
        
        return results
        
    except Exception as e:
        # On connection error, try to return mostly relevant cached data if possible or empty
        return cache.get(keyword, {}).get("results", [{"error": str(e)}])


def format_cve_results(results: List[Dict]) -> str:
    """Format CVE results for display."""
    if not results:
        return "No CVEs found."
    
    if "error" in results[0]:
        return f"Error: {results[0]['error']}"
    
    output = "🔒 CVE LOOKUP RESULTS\n"
    output += "=" * 50 + "\n\n"
    
    for cve in results:
        severity_color = {
            "CRITICAL": "🔴",
            "HIGH": "🟠", 
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }.get(cve["severity"], "⚪")
        
        output += f"{severity_color} {cve['id']} (Score: {cve['score']})\n"
        output += f"   Severity: {cve['severity']}\n"
        output += f"   {cve['description']}\n\n"
    
    return output
