# ============================================================
# resume_data.py
# Your REAL experience, skills, projects, certs
# This file is the ONLY place you edit your actual content
# The tailor script reads from here — it never invents content
# ============================================================

PERSONAL = {
    "name": "KHADER SHAREEF",
    "role_label": "SOC Analyst",  # default, tailoring can swap this
    "location": "Hyderabad, Telangana, India",
    "phone": "+91 9515787655",
    "email": "infa.khadershareef@gmail.com",
    "linkedin": "https://www.linkedin.com/in/khader-shareef-madani-129167260",
    "github": "https://github.com/KHADERSHAREEF19",
    "portfolio": "https://khadershareef19.vercel.app",
}

# Default summary — tailoring script adjusts the target role
SUMMARY_TEMPLATE = (
    "{role_title} with hands-on experience in multi-tenant SOC operations, "
    "specializing in alert triage, incident investigation and first-response "
    "containment using Microsoft Sentinel and Microsoft Defender XDR. Skilled "
    "in phishing and BEC investigation, email-header analysis, IOC enrichment, "
    "KQL-based log analysis and SLA-driven incident reporting. "
    "{cert_line}"
)

CERTS_SHORT = "Cisco CCNA, CompTIA Network+ and ISC2 CC"
CERT_LINE = f"Holds {CERTS_SHORT} certifications."

# Certifications — order will be adjusted based on JD
CERTIFICATIONS = [
    {"name": "Cisco Certified Network Associate (CCNA)", "status": "earned",
     "keywords": ["ccna", "cisco", "networking", "network"]},

    {"name": "CompTIA Network+", "status": "earned",
     "keywords": ["comptia", "network+", "networking"]},

    {"name": "ISC2 Certified in Cybersecurity (CC)", "status": "earned",
     "keywords": ["isc2", "cc", "cybersecurity"]},

    {"name": "Certified Blue Team Practitioner (CBTP) — The SecOps Group",
     "status": "earned",
     "keywords": ["blue team", "cbtp", "defensive"]},

    {"name": "SOC Level 1 — TryHackMe", "status": "earned",
     "keywords": ["soc", "tryhackme", "soc analyst"]},

    {"name": "Certified Network Security Practitioner (CNSP) — The SecOps Group",
     "status": "earned",
     "keywords": ["cnsp", "network security"]},

    {"name": "Certified Social Engineering Defence Practitioner (CSEDP) — The SecOps Group",
     "status": "earned",
     "keywords": ["social engineering", "csedp"]},

    {"name": "DevSecOps — TryHackMe", "status": "earned",
     "keywords": ["devsecops", "cicd", "pipeline"]},

    {"name": "Fundamentals of Cybersecurity — IBM", "status": "earned",
     "keywords": ["ibm", "cybersecurity fundamentals"]},
]

# Skills — grouped with keywords for matching
# "level" controls honesty: "production", "lab", "basic", "learning"
SKILLS = {
    "SOC Operations": [
        {"skill": "Alert Triage", "level": "production", "keywords": ["alert triage", "triage"]},
        {"skill": "Incident Management", "level": "production", "keywords": ["incident management"]},
        {"skill": "Incident Investigation", "level": "production", "keywords": ["incident investigation", "investigation"]},
        {"skill": "Incident Response", "level": "production", "keywords": ["incident response", "ir"]},
        {"skill": "Threat Detection", "level": "production", "keywords": ["threat detection", "detection"]},
        {"skill": "Security Monitoring", "level": "production", "keywords": ["security monitoring", "monitoring"]},
        {"skill": "Containment", "level": "production", "keywords": ["containment"]},
        {"skill": "Remediation", "level": "production", "keywords": ["remediation"]},
        {"skill": "Log Analysis", "level": "production", "keywords": ["log analysis", "log review"]},
        {"skill": "Phishing/BEC Analysis", "level": "production", "keywords": ["phishing", "bec", "email security"]},
        {"skill": "Email Security", "level": "production", "keywords": ["email security", "email"]},
        {"skill": "Identity Security", "level": "production", "keywords": ["identity security", "identity"]},
        {"skill": "IOC Enrichment", "level": "production", "keywords": ["ioc", "indicator of compromise", "threat intel"]},
        {"skill": "MITRE ATT&CK", "level": "production", "keywords": ["mitre", "att&ck", "mitre att&ck"]},
    ],
    "Microsoft Security": [
        {"skill": "Microsoft Sentinel", "level": "production", "keywords": ["sentinel", "azure sentinel", "microsoft sentinel"]},
        {"skill": "Microsoft Defender XDR (MDE, MDO, MDI, MDCA)", "level": "production",
         "keywords": ["defender xdr", "mde", "mdo", "mdi", "mdca", "defender"]},
        {"skill": "Entra ID", "level": "production", "keywords": ["entra id", "azure ad", "entra"]},
        {"skill": "KQL", "level": "production", "keywords": ["kql", "kusto"]},
        {"skill": "EDR", "level": "production", "keywords": ["edr", "endpoint detection"]},
    ],
    "SIEM & Detection (Lab Exposure)": [
        {"skill": "Splunk", "level": "lab", "keywords": ["splunk"]},
        {"skill": "Wazuh", "level": "lab", "keywords": ["wazuh"]},
    ],
    "Threat Intelligence & Security Tools": [
        {"skill": "VirusTotal", "level": "production", "keywords": ["virustotal"]},
        {"skill": "AbuseIPDB", "level": "production", "keywords": ["abuseipdb"]},
        {"skill": "Wireshark", "level": "lab", "keywords": ["wireshark", "packet capture", "pcap"]},
        {"skill": "Nmap", "level": "lab", "keywords": ["nmap", "network scanning"]},
        {"skill": "Nessus", "level": "lab", "keywords": ["nessus", "vulnerability scan"]},
        {"skill": "Metasploit", "level": "lab", "keywords": ["metasploit", "penetration testing"]},
    ],
    "Networking & Systems": [
        {"skill": "TCP/IP", "level": "production", "keywords": ["tcp/ip", "tcp", "ip"]},
        {"skill": "DNS", "level": "production", "keywords": ["dns"]},
        {"skill": "HTTP/HTTPS", "level": "production", "keywords": ["http", "https"]},
        {"skill": "Active Directory", "level": "production", "keywords": ["active directory", "ad"]},
        {"skill": "Windows", "level": "production", "keywords": ["windows"]},
        {"skill": "Linux (Ubuntu, Arch)", "level": "production", "keywords": ["linux", "ubuntu"]},
        {"skill": "Fortinet FortiGate Firewalls", "level": "basic",
         "keywords": ["fortigate", "fortinet", "firewall", "firewalls"]},
    ],
    "Scripting & Automation": [
        {"skill": "Python (Basic)", "level": "basic", "keywords": ["python"]},
        {"skill": "SQL", "level": "basic", "keywords": ["sql"]},
        {"skill": "Bash", "level": "basic", "keywords": ["bash", "shell"]},
        {"skill": "Git/GitHub", "level": "production", "keywords": ["git", "github"]},
        {"skill": "n8n", "level": "basic", "keywords": ["n8n", "automation"]},
        {"skill": "Docker", "level": "basic", "keywords": ["docker", "container"]},
    ],
}

# Experience — each bullet tagged with keywords for reordering
EXPERIENCE = [
    {
        "title": "AI Threat Validation Analyst (SOC Operations)",
        "company": "Cyber Managed Services Inc",
        "dates": "June 2026 – July 2026",   # UPDATE TO REAL DATES
        "location": "Chicago, USA (Remote) | Enterprise Multi-Tenant SOC",
        "bullets": [
            {
                "text": "Triaged real-time alerts in Microsoft Sentinel and Microsoft Defender XDR across multiple client tenants, correlating endpoint, email and identity telemetry to classify True Positives and False Positives.",
                "keywords": ["sentinel", "defender xdr", "triage", "alert", "true positive", "false positive", "endpoint", "email", "identity"],
                "priority": 1,
                "pin": True,
            },
            {
                "text": "Investigated phishing and Business Email Compromise (BEC) incidents through email-header analysis (SPF, DKIM and DMARC), sandbox results and IOC reputation checks using VirusTotal and AbuseIPDB.",
                "keywords": ["phishing", "bec", "spf", "dkim", "dmarc", "ioc", "virustotal", "abuseipdb", "email"],
                "priority": 2,
            },
            {
                "text": "Performed first-response containment for confirmed threats, including host network isolation, malicious-file quarantine and active-session revocation to reduce account-takeover and lateral-movement risk.",
                "keywords": ["containment", "isolation", "quarantine", "incident response", "lateral movement"],
                "priority": 3,
            },
            {
                "text": "Used KQL in Microsoft Sentinel to review security logs, validate alert findings and scope affected users, endpoints and activity.",
                "keywords": ["kql", "sentinel", "log analysis", "kusto"],
                "priority": 4,
            },
            {
                "text": "Documented investigations in structured 5W incident reports within client SLAs and SOPs, providing evidence, timelines, impact scope and remediation recommendations for escalation.",
                "keywords": ["documentation", "sla", "sop", "incident report", "5w", "escalation"],
                "priority": 5,
            },
        ],
    },
    {
        "title": "Cyber Security Analyst",
        "company": "DigiSuraksha Parhari Foundation",
        "dates": "July 2024 – August 2024",
        "location": "Gurugram, India | SOC Environment",
        "bullets": [
            {
                "text": "Monitored and triaged 500+ daily SIEM alerts, identifying suspicious activity patterns and escalating potential security incidents for investigation.",
                "keywords": ["siem", "alert", "triage", "monitoring", "escalation"],
                "priority": 1,
            },
            {
                "text": "Conducted initial investigations into malware infections, phishing attempts and unauthorized-access events, documenting evidence and findings in incident-tracking systems.",
                "keywords": ["malware", "phishing", "investigation", "unauthorized access", "documentation"],
                "priority": 2,
            },
            {
                "text": "Collaborated with the security team on threat containment, remediation and vulnerability-mitigation activities across organizational digital assets.",
                "keywords": ["containment", "remediation", "vulnerability", "collaboration"],
                "priority": 3,
            },
        ],
    },
]

# Projects — tagged for reordering
PROJECTS = [
    {
        "name": "CereloX",
        "url": "https://github.com/KHADERSHAREEF19/CereLox",
        "subtitle": ": Windows Event Log Analysis & Visualization Tool (Python)",
        "bullets": [
            {
                "text": "Built a Python-based tool to parse and visualize Windows Event Logs, accelerating incident triage and forensic review of authentication activity.",
                "keywords": ["python", "windows event log", "forensic", "triage", "log analysis"],
            },
            {
                "text": "Detected unauthorized-login attempts with 95% accuracy across 15+ simulated brute-force attack patterns.",
                "keywords": ["brute force", "detection", "authentication", "accuracy"],
            },
        ],
    },
    {
        "name": "Home Lab",
        "url": "https://github.com/KHADERSHAREEF19/SOC-HOME_LAB",
        "subtitle": ": SOC Detection & Response Environment",
        "bullets": [
            {
                "text": "Built a virtualized SOC lab using Kali Linux, Ubuntu Server and Windows 10 Pro to simulate attack scenarios and practise end-to-end detection, investigation and response.",
                "keywords": ["soc", "lab", "kali", "linux", "detection", "investigation"],
            },
            {
                "text": "Used Splunk and Wazuh in a lab environment to identify brute-force and suspicious-login activity, review logs and analyse packet captures with Wireshark.",
                "keywords": ["splunk", "wazuh", "wireshark", "brute force", "packet capture", "siem"],
            },
        ],
    },
    {
        "name": "SecureWipe",
        "url": "https://github.com/KHADERSHAREEF19/Secure-Wipe",
        "subtitle": ": Data Sanitization Tool | Smart India Internal Hackathon 2025 Finalist",
        "bullets": [
            {
                "text": "Developed a secure data-sanitization solution designed to permanently erase sensitive data and prevent forensic recovery.",
                "keywords": ["data sanitization", "forensic", "security", "data protection"],
            },
            {
                "text": "Improved wiping performance by 25% over baseline methods through multi-threaded disk I/O operations.",
                "keywords": ["performance", "multithreaded", "optimization"],
            },
        ],
    },
]

EDUCATION = {
    "degree": "Bachelor of Engineering, Computer Science & Engineering (Cybersecurity)",
    "university": "Osmania University",
    "dates": "Nov 2022 – June 2026",
    "location": "Hyderabad, India",
    "cgpa": "CGPA: 8.19/10",
}

ACHIEVEMENTS = [
    "Secured 3rd Rank for Academic Excellence in B.E. CSE (Cybersecurity) across all Osmania University-affiliated colleges in Telangana.",
    "Smart India Hackathon (SIH) 2025 Internal Hackathon Finalist for SecureWipe, a secure data-sanitization solution.",
    "President, Cyber Elites Club, Osmania University (June 2023 – June 2026): grew membership by 30%, organized 6+ technical events including a 150+ participant CTF, and mentored 70+ students on cybersecurity concepts and certification roadmaps.",
]

# Role title alternatives that the tailoring script can swap
# based on the JD title. Only use titles that honestly describe
# the same SOC work you performed.
ACCEPTABLE_ROLE_TITLES = [
    "SOC Analyst",
    "Security Operations Analyst",
    "Cybersecurity Analyst",
    "Security Analyst",
    "Threat Analyst",
    "Incident Response Analyst",
    "Blue Team Analyst",
]