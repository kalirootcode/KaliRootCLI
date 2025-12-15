"""
Port Scanner Tool - Premium Feature
Simple socket-based scanner with AI analysis.
"""

import socket
import concurrent.futures
from typing import List, Dict

# Common ports to scan
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
    1723, 3306, 3389, 5432, 5900, 8080, 8443, 8888, 27017
]

PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1723: "PPTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    5900: "VNC", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "HTTP-Alt",
    27017: "MongoDB"
}


def scan_port(host: str, port: int, timeout: float = 1.0) -> Dict:
    """Scan a single port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return {
                "port": port,
                "status": "open",
                "service": PORT_SERVICES.get(port, "unknown")
            }
        return None
    except:
        return None


def quick_scan(host: str, ports: List[int] = None, timeout: float = 0.5) -> List[Dict]:
    """
    Scan multiple ports concurrently.
    Returns list of open ports with their services.
    """
    if ports is None:
        ports = COMMON_PORTS
    
    open_ports = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(scan_port, host, port, timeout): port for port in ports}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
    
    return sorted(open_ports, key=lambda x: x["port"])


def format_scan_results(host: str, results: List[Dict]) -> str:
    """Format scan results for display."""
    if not results:
        return f"No open ports found on {host}"
    
    output = f"🔍 Scan Results for {host}\n"
    output += "=" * 40 + "\n\n"
    
    for r in results:
        output += f"  Port {r['port']:>5} │ {r['status']:>6} │ {r['service']}\n"
    
    output += f"\n📊 Total: {len(results)} open ports"
    return output
