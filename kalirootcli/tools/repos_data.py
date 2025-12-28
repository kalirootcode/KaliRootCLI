"""
Database of Top 100+ Ethical Hacking Repositories.
Verified list of high-impact tools.
"""

TOP_REPOS = [
    # ─── RECONNAISSANCE ───
    {"name": "Nmap", "url": "https://github.com/nmap/nmap", "category": "Recon"},
    {"name": "Sherlock", "url": "https://github.com/sherlock-project/sherlock", "category": "Recon"},
    {"name": "TheHarvester", "url": "https://github.com/laramies/theHarvester", "category": "Recon"},
    {"name": "Sublist3r", "url": "https://github.com/aboul3la/Sublist3r", "category": "Recon"},
    {"name": "Amass", "url": "https://github.com/owasp-amass/amass", "category": "Recon"},
    {"name": "Photon", "url": "https://github.com/s0md3v/Photon", "category": "Recon"},
    {"name": "Assetfinder", "url": "https://github.com/tomnomnom/assetfinder", "category": "Recon"},
    {"name": "Httprobe", "url": "https://github.com/tomnomnom/httprobe", "category": "Recon"},
    {"name": "Waybackurls", "url": "https://github.com/tomnomnom/waybackurls", "category": "Recon"},
    {"name": "Gau", "url": "https://github.com/lc/gau", "category": "Recon"},

    # ─── VULNERABILITY ANALYSIS ───
    {"name": "Nuclei", "url": "https://github.com/projectdiscovery/nuclei", "category": "Vuln Analysis"},
    {"name": "Nikto", "url": "https://github.com/sullo/nikto", "category": "Vuln Analysis"},
    {"name": "Wapiti", "url": "https://github.com/wapiti-scanner/wapiti", "category": "Vuln Analysis"},
    {"name": "OpenVAS", "url": "https://github.com/greenbone/openvas-scanner", "category": "Vuln Analysis"},
    {"name": "Arachni", "url": "https://github.com/Arachni/arachni", "category": "Vuln Analysis"},
    {"name": "Vuls", "url": "https://github.com/future-architect/vuls", "category": "Vuln Analysis"},
    
    # ─── WEB EXPLOITATION ───
    {"name": "Sqlmap", "url": "https://github.com/sqlmapproject/sqlmap", "category": "Web Exploit"},
    {"name": "XSSer", "url": "https://github.com/epsylon/xsser", "category": "Web Exploit"},
    {"name": "Wfuzz", "url": "https://github.com/xmendez/wfuzz", "category": "Web Exploit"},
    {"name": "FFUF", "url": "https://github.com/ffuf/ffuf", "category": "Web Exploit"},
    {"name": "Commix", "url": "https://github.com/commixproject/commix", "category": "Web Exploit"},
    {"name": "WhatWaf", "url": "https://github.com/Ekultek/WhatWaf", "category": "Web Exploit"},
    {"name": "XSStrike", "url": "https://github.com/s0md3v/XSStrike", "category": "Web Exploit"},
    {"name": "Dalfox", "url": "https://github.com/hahwul/dalfox", "category": "Web Exploit"},
    {"name": "JoomScan", "url": "https://github.com/rezasp/joomscan", "category": "Web Exploit"},
    {"name": "WPScan", "url": "https://github.com/wpscanteam/wpscan", "category": "Web Exploit"},

    # ─── EXPLOITATION FRAMEWORKS ───
    {"name": "Metasploit", "url": "https://github.com/rapid7/metasploit-framework", "category": "Exploitation"},
    {"name": "ExploitDB", "url": "https://github.com/offensive-security/exploitdb", "category": "Exploitation"},
    {"name": "RouterSploit", "url": "https://github.com/threat9/routersploit", "category": "Exploitation"},
    {"name": "Poupou", "url": "https://github.com/n1nj4sec/pupy", "category": "Exploitation"},
    {"name": "Sliver", "url": "https://github.com/BishopFox/sliver", "category": "Exploitation"},
    
    # ─── PASSWORD ATTACKS ───
    {"name": "Hydra", "url": "https://github.com/vanhauser-thc/thc-hydra", "category": "Passwords"},
    {"name": "John the Ripper", "url": "https://github.com/openwall/john", "category": "Passwords"},
    {"name": "Hashcat", "url": "https://github.com/hashcat/hashcat", "category": "Passwords"},
    {"name": "SecLists", "url": "https://github.com/danielmiessler/SecLists", "category": "Wordlists"},
    {"name": "Patator", "url": "https://github.com/lanjelot/patator", "category": "Passwords"},
    {"name": "Crowbar", "url": "https://github.com/galkan/crowbar", "category": "Passwords"},

    # ─── WIRELESS & NETWORK ───
    {"name": "Aircrack-ng", "url": "https://github.com/aircrack-ng/aircrack-ng", "category": "Wireless"},
    {"name": "Wifite2", "url": "https://github.com/derv82/wifite2", "category": "Wireless"},
    {"name": "Kismet", "url": "https://github.com/kismetwireless/kismet", "category": "Wireless"},
    {"name": "Fluxion", "url": "https://github.com/FluxionNetwork/fluxion", "category": "Wireless"},
    {"name": "Airgeddon", "url": "https://github.com/v1s1t0r1sh3r3/airgeddon", "category": "Wireless"},
    {"name": "Bettercap", "url": "https://github.com/bettercap/bettercap", "category": "Network"},
    {"name": "Wireshark", "url": "https://github.com/wireshark/wireshark", "category": "Network"},
    {"name": "Tcpdump", "url": "https://github.com/the-tcpdump-group/tcpdump", "category": "Network"},
    {"name": "Responder", "url": "https://github.com/lgandx/Responder", "category": "Network"},
    {"name": "Ettercap", "url": "https://github.com/Ettercap/ettercap", "category": "Network"},
    {"name": "Mitmproxy", "url": "https://github.com/mitmproxy/mitmproxy", "category": "Network"},
    {"name": "Netcat", "url": "https://github.com/nmap/nmap", "category": "Network"}, # Often distributed with nmap source

    # ─── POST-EXPLOITATION & C2 ───
    {"name": "Empire", "url": "https://github.com/BC-SECURITY/Empire", "category": "Post-Exploit"},
    {"name": "Mimikatz", "url": "https://github.com/ParrotSec/mimikatz", "category": "Post-Exploit"},
    {"name": "PowerSploit", "url": "https://github.com/PowerShellMafia/PowerSploit", "category": "Post-Exploit"},
    {"name": "CrackMapExec", "url": "https://github.com/byt3bl33d3r/CrackMapExec", "category": "Post-Exploit"},
    {"name": "Impacket", "url": "https://github.com/fortra/impacket", "category": "Post-Exploit"},
    {"name": "BloodHound", "url": "https://github.com/BloodHoundAD/BloodHound", "category": "Post-Exploit"},
    {"name": "Evil-WinRM", "url": "https://github.com/Hackplayers/evil-winrm", "category": "Post-Exploit"},
    {"name": "LaZagne", "url": "https://github.com/AlessandroZ/LaZagne", "category": "Post-Exploit"},
    {"name": "PwnCat", "url": "https://github.com/calebstewart/pwncat", "category": "Post-Exploit"},

    # ─── OSINT ───
    {"name": "Osintgram", "url": "https://github.com/Datalux/Osintgram", "category": "OSINT"},
    {"name": "Spiderfoot", "url": "https://github.com/smicallef/spiderfoot", "category": "OSINT"},
    {"name": "Recon-ng", "url": "https://github.com/lanmaster53/recon-ng", "category": "OSINT"},
    {"name": "PhoneInfoga", "url": "https://github.com/sundowndev/phoneinfoga", "category": "OSINT"},
    {"name": "Sherlock", "url": "https://github.com/sherlock-project/sherlock", "category": "OSINT"}, # Listed in recon too, but fits
    {"name": "Twint", "url": "https://github.com/twintproject/twint", "category": "OSINT"},
    {"name": "H8mail", "url": "https://github.com/khast3x/h8mail", "category": "OSINT"},
    {"name": "Ghunt", "url": "https://github.com/mxrch/GHunt", "category": "OSINT"},
    {"name": "Shodan CLI", "url": "https://github.com/achillean/shodan-python", "category": "OSINT"},

    # ─── MOBILE & ANDROID ───
    {"name": "MobSF", "url": "https://github.com/MobSF/Mobile-Security-Framework-MobSF", "category": "Mobile"},
    {"name": "AndroRAT", "url": "https://github.com/karma9874/AndroRAT", "category": "Mobile"},
    {"name": "APKTool", "url": "https://github.com/iBotPeaches/Apktool", "category": "Mobile"},
    {"name": "Drozer", "url": "https://github.com/WithSecureLabs/drozer", "category": "Mobile"},
    {"name": "Frida", "url": "https://github.com/frida/frida", "category": "Mobile"},
    {"name": "Objection", "url": "https://github.com/sensepost/objection", "category": "Mobile"},
    {"name": "QARK", "url": "https://github.com/linkedin/qark", "category": "Mobile"},

    # ─── REVERSE ENGINEERING ───
    {"name": "Ghidra", "url": "https://github.com/NationalSecurityAgency/ghidra", "category": "Reverse Eng"},
    {"name": "Radare2", "url": "https://github.com/radareorg/radare2", "category": "Reverse Eng"},
    {"name": "X64dbg", "url": "https://github.com/x64dbg/x64dbg", "category": "Reverse Eng"},
    {"name": "Cutter", "url": "https://github.com/rizinorg/cutter", "category": "Reverse Eng"},
    {"name": "Pwndbg", "url": "https://github.com/pwndbg/pwndbg", "category": "Reverse Eng"},

    # ─── CLOUD SECURITY ───
    {"name": "Prowler", "url": "https://github.com/prowler-cloud/prowler", "category": "Cloud"},
    {"name": "ScoutSuite", "url": "https://github.com/nccgroup/ScoutSuite", "category": "Cloud"},
    {"name": "Clouds", "url": "https://github.com/awslabs/git-secrets", "category": "Cloud"},
    {"name": "CloudSploit", "url": "https://github.com/aquasecurity/cloudsploit", "category": "Cloud"},
    
    # ─── PRIVILEGE ESCALATION ───
    {"name": "PEASS-ng", "url": "https://github.com/carlospolop/PEASS-ng", "category": "PrivEsc"},
    {"name": "LinEnum", "url": "https://github.com/rebootuser/LinEnum", "category": "PrivEsc"},
    {"name": "GTFOBins", "url": "https://github.com/GTFOBins/GTFOBins.github.io", "category": "PrivEsc"},
    {"name": "Windows-Exploit-Suggester", "url": "https://github.com/AonCyberLabs/Windows-Exploit-Suggester", "category": "PrivEsc"},
    {"name": "Linux-Exploit-Suggester", "url": "https://github.com/mzet-/linux-exploit-suggester", "category": "PrivEsc"},

    # ─── SOCIAL ENGINEERING & PHISHING ───
    {"name": "Social Eng Toolkit", "url": "https://github.com/trustedsec/social-engineer-toolkit", "category": "Social Eng"},
    {"name": "Gophish", "url": "https://github.com/gophish/gophish", "category": "Social Eng"},
    {"name": "KingPhisher", "url": "https://github.com/rsmusllp/king-phisher", "category": "Social Eng"},
    {"name": "Zphisher", "url": "https://github.com/htr-tech/zphisher", "category": "Social Eng"},
    {"name": "SocialFish", "url": "https://github.com/UndeadSec/SocialFish", "category": "Social Eng"},

    # ─── EDUCATIONAL ───
    {"name": "DVWA", "url": "https://github.com/digininja/DVWA", "category": "Educational"},
    {"name": "Juice Shop", "url": "https://github.com/juice-shop/juice-shop", "category": "Educational"},
    {"name": "Metasploitable3", "url": "https://github.com/rapid7/metasploitable3", "category": "Educational"},
    {"name": "SecGen", "url": "https://github.com/cliffe/SecGen", "category": "Educational"},

    # ─── ANONYMITY ───
    {"name": "ProxyChains", "url": "https://github.com/haad/proxychains", "category": "Anonymity"},
    {"name": "Tor", "url": "https://github.com/torproject/tor", "category": "Anonymity"},
    {"name": "Kalitorify", "url": "https://github.com/brainfucksec/kalitorify", "category": "Anonymity"},
    # Nipe removed - repository no longer maintained

    # ─── MISC / UTILS ───
    {"name": "PayloadAllTheThings", "url": "https://github.com/swisskyrepo/PayloadsAllTheThings", "category": "Resources"},
    {"name": "PwnTools", "url": "https://github.com/Gallopsled/pwntools", "category": "Utils"},
    {"name": "Scapy", "url": "https://github.com/secdev/scapy", "category": "Utils"},
    {"name": "CyberChef", "url": "https://github.com/gchq/CyberChef", "category": "Utils"},
    {"name": "Yara", "url": "https://github.com/VirusTotal/yara", "category": "Utils"},

    # ─── LABS & TRAINING ───
    # Note: Many HTB/THM scripts repos are private or removed
    {"name": "Awesome-Hacking", "url": "https://github.com/Hack-with-Github/Awesome-Hacking", "category": "Resources"},
    {"name": "Hacking Resources", "url": "https://github.com/vitalysim/Awesome-Hacking-Resources", "category": "Resources"},

    # ─── GOOGLE DRIVE ───
    {"name": "Gdown (GDrive Downloader)", "url": "https://github.com/wkentaro/gdown", "category": "Utils"},
    
    # ─── FORENSICS ───
    {"name": "Binwalk", "url": "https://github.com/ReFirmLabs/binwalk", "category": "Forensics"},
    {"name": "Foremost", "url": "https://github.com/korczis/foremost", "category": "Forensics"},
    {"name": "Scalpel", "url": "https://github.com/sleuthkit/scalpel", "category": "Forensics"},
    # Caine removed - not a GitHub repository (distributed as ISO from caine-live.net)
    {"name": "Autopsy", "url": "https://github.com/sleuthkit/autopsy", "category": "Forensics"},

    # ─── TERMUX UTILS ───
    {"name": "Termux-API", "url": "https://github.com/termux/termux-api", "category": "Termux"},
    {"name": "Termux-Styling", "url": "https://github.com/termux/termux-styling", "category": "Termux"},
    {"name": "LazyMux", "url": "https://github.com/Gameye98/Lazymux", "category": "Termux"},
    {"name": "Katoolin", "url": "https://github.com/LionSec/katoolin", "category": "Termux"},
]
