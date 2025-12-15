"""
CVE Lookup Tool - Premium Feature
Search CVE database via NIST NVD API.
"""

import requests
from typing import Dict, List, Optional

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def search_cve(keyword: str, limit: int = 5) -> List[Dict]:
    """
    Search CVE database by keyword.
    Returns list of CVEs with id, description, severity.
    """
    try:
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": limit
        }
        
        response = requests.get(NVD_API, params=params, timeout=15)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
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
        
        return results
        
    except Exception as e:
        return [{"error": str(e)}]


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
