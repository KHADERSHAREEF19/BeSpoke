# ============================================================
# resume_data.py
# Your REAL experience, skills, projects, certs
# This file is the ONLY place you edit your actual content
# The tailor script reads from here — it never invents content
#
# Synced with KhaderShareef_UAE_Resume.pdf
# ============================================================

PERSONAL = {
    "name": "KHADER SHAREEF",
    "role_label": "Cybersecurity Analyst",  # default, tailoring can swap this
    "location": "Hyderabad, Telangana, India",
    "phone": "+91 9515787655",
    "uae_phone": "+971 56 951 5117",       # shown alongside the India number
    "email": "infa.khadershareef@gmail.com",
    "linkedin": "https://www.linkedin.com/in/khader-shareef-madani-129167260",
    "github": "https://github.com/KHADERSHAREEF19",
    "portfolio": "https://khadershareef19.vercel.app",
}

# Default summary — tailoring script adjusts the target role
SUMMARY_TEMPLATE = (
    "{role_title} with hands-on technical experience in enterprise 24/7 "
    "multi-tenant SOC environments, specializing in cross-vector threat triage "
    "across Microsoft Defender XDR and Microsoft Sentinel, rapid incident "
    "containment and KQL-based log analysis. Currently working with PingOne "
    "and Microsoft Entra ID on SSO, MFA and identity security. {cert_line}"
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
    "Security Operations": [
        {"skill": "Alert Triage", "level": "production", "keywords": ["alert triage", "triage"]},
        {"skill": "Threat Triage", "level": "production", "keywords": ["threat triage", "triage"]},
        {"skill": "Incident Management", "level": "production", "keywords": ["incident management"]},
        {"skill": "Incident Response", "level": "production", "keywords": ["incident response", "ir"]},
        {"skill": "Incident Investigation", "level": "production", "keywords": ["incident investigation", "investigation"]},
        {"skill": "Security Monitoring", "level": "production", "keywords": ["security monitoring", "monitoring"]},
        {"skill": "Threat Detection", "level": "production", "keywords": ["threat detection", "detection"]},
        {"skill": "Containment", "level": "production", "keywords": ["containment"]},
        {"skill": "Remediation", "level": "production", "keywords": ["remediation"]},
        {"skill": "Log Analysis", "level": "production", "keywords": ["log analysis", "log review"]},
        {"skill": "Phishing/BEC Analysis", "level": "production", "keywords": ["phishing", "bec", "email security"]},
        {"skill": "Email Security", "level": "production", "keywords": ["email security", "email"]},
        {"skill": "IOC Enrichment", "level": "production", "keywords": ["ioc", "indicator of compromise", "threat intel"]},
        {"skill": "MITRE ATT&CK", "level": "production", "keywords": ["mitre", "att&ck", "mitre att&ck"]},
        {"skill": "EDR", "level": "production", "keywords": ["edr", "endpoint detection"]},
    ],
    "SIEM & Detection": [
        {"skill": "Microsoft Sentinel", "level": "production",
         "keywords": ["sentinel", "azure sentinel", "microsoft sentinel", "siem"]},
        {"skill": "Splunk", "level": "lab", "keywords": ["splunk"]},
        {"skill": "Wazuh", "level": "lab", "keywords": ["wazuh"]},
    ],
    "Microsoft Security": [
        {"skill": "Microsoft Defender XDR (MDE, MDO, MDI, MDCA)", "level": "production",
         "keywords": ["defender xdr", "mde", "mdo", "mdi", "mdca", "defender"]},
        {"skill": "KQL", "level": "production", "keywords": ["kql", "kusto"]},
    ],
    "Identity & Access Management": [
        {"skill": "PingOne Workforce", "level": "production",
         "keywords": ["pingone", "workforce", "ping"]},
        {"skill": "PingOne Protect", "level": "production",
         "keywords": ["pingone", "protect", "adaptive mfa"]},
        {"skill": "PingOne DaVinci", "level": "production",
         "keywords": ["pingone", "davinci", "identity workflow"]},
        {"skill": "PingOne Verify", "level": "production",
         "keywords": ["pingone", "verify", "identity proofing"]},
        {"skill": "Microsoft Entra ID", "level": "production",
         "keywords": ["entra id", "azure ad", "entra"]},
        {"skill": "SSO (Single Sign-On)", "level": "production",
         "keywords": ["sso", "single sign-on", "single sign on"]},
        {"skill": "SAML 2.0", "level": "production", "keywords": ["saml"]},
        {"skill": "OIDC", "level": "production", "keywords": ["oidc", "openid connect"]},
        {"skill": "MFA", "level": "production", "keywords": ["mfa", "multi-factor", "multi-factor authentication"]},
        {"skill": "RBAC", "level": "production", "keywords": ["rbac", "role-based access control"]},
        {"skill": "Customer IAM (CIAM)", "level": "basic", "keywords": ["ciam", "customer iam"]},
        {"skill": "Privileged Access Management (PAM) — PingAM", "level": "basic",
         "keywords": ["pam", "privileged access", "pingam"]},
        {"skill": "Okta", "level": "basic", "keywords": ["okta"]},
        {"skill": "Saviynt", "level": "basic", "keywords": ["saviynt"]},
    ],
    "Network & Perimeter Security": [
        {"skill": "Fortinet FortiGate Firewalls", "level": "basic",
         "keywords": ["fortigate", "fortinet", "firewall", "firewalls"]},
        {"skill": "TCP/IP", "level": "production", "keywords": ["tcp/ip", "tcp", "ip"]},
        {"skill": "Active Directory", "level": "production", "keywords": ["active directory", "ad"]},
        {"skill": "DNS", "level": "production", "keywords": ["dns"]},
        {"skill": "VPN", "level": "basic", "keywords": ["vpn", "virtual private network"]},
        {"skill": "Wireshark", "level": "lab", "keywords": ["wireshark", "packet capture", "pcap"]},
        {"skill": "Nmap", "level": "lab", "keywords": ["nmap", "network scanning"]},
    ],
    "Threat Intelligence & Security Tools": [
        {"skill": "VirusTotal", "level": "production", "keywords": ["virustotal"]},
        {"skill": "AbuseIPDB", "level": "production", "keywords": ["abuseipdb"]},
        {"skill": "Nessus", "level": "lab", "keywords": ["nessus", "vulnerability scan"]},
        {"skill": "Metasploit", "level": "lab", "keywords": ["metasploit", "penetration testing"]},
    ],
    "Programming & Automation": [
        {"skill": "Python", "level": "production", "keywords": ["python"]},
        {"skill": "SQL", "level": "basic", "keywords": ["sql"]},
        {"skill": "Bash", "level": "basic", "keywords": ["bash", "shell"]},
        {"skill": "Git/GitHub", "level": "production", "keywords": ["git", "github"]},
        {"skill": "Docker", "level": "basic", "keywords": ["docker", "container"]},
        {"skill": "n8n", "level": "basic", "keywords": ["n8n", "automation"]},
        {"skill": "OpenClaw", "level": "basic", "keywords": ["openclaw"]},
        {"skill": "Claude", "level": "basic", "keywords": ["claude", "ai assistant"]},
    ],
    "Cloud & Infrastructure": [
        {"skill": "AWS", "level": "basic", "keywords": ["aws", "amazon web services"]},
        {"skill": "Azure", "level": "production", "keywords": ["azure", "microsoft azure"]},
        {"skill": "Linux (Ubuntu, Arch)", "level": "production", "keywords": ["linux", "ubuntu"]},
        {"skill": "Windows Server (2019/2022)", "level": "basic", "keywords": ["windows server", "server 2019", "server 2022"]},
    ],
}

# Experience — each bullet tagged with keywords for reordering
EXPERIENCE = [
    {
        "title": "Identity & Access Management (IAM) Intern",
        "company": "North Star Identity",
        "dates": "October 2026 – Present",
        "location": "Texas, USA (Remote) | Enterprise IAM",
        "bullets": [
            {
                "text": "Configured enterprise Single Sign-On (SSO) integrations on PingOne Workforce using OIDC and SAML 2.0, managing user directories, custom attributes and Role-Based Access Control (RBAC) policies.",
                "keywords": ["pingone", "workforce", "sso", "oidc", "saml", "rbac", "directories", "attributes"],
                "priority": 1,
            },
            {
                "text": "Configured adaptive Multi-Factor Authentication (MFA) and threat-protection rules in PingOne Protect, applying risk-based step-up authentication driven by contextual risk signals and suspicious activity.",
                "keywords": ["pingone", "protect", "mfa", "adaptive", "step-up", "risk", "authentication"],
                "priority": 2,
            },
            {
                "text": "Built identity workflows in PingOne DaVinci and integrated PingOne Verify for identity proofing (ID and selfie verification); reviewed platform audit logs to troubleshoot authentication failures.",
                "keywords": ["pingone", "davinci", "verify", "identity proofing", "audit logs", "troubleshoot", "authentication"],
                "priority": 3,
            },
        ],
    },
    {
        "title": "AI Threat Validation Analyst (SOC Operations)",
        "company": "Cyber Managed Services Inc",
        "dates": "June 2026 – July 2026",
        "location": "Chicago, USA (Remote) | Enterprise Multi-Tenant SOC",
        "bullets": [
            {
                "text": "Monitored real-time alert streams across enterprise multi-tenant environments using Microsoft Sentinel and Microsoft Defender XDR platforms.",
                "keywords": ["sentinel", "defender xdr", "monitoring", "alert", "multi-tenant", "soc"],
                "priority": 1,
                "pin": True,
            },
            {
                "text": "Conducted precise incident qualification to separate True Positives from False Positives across endpoint, email and identity telemetry.",
                "keywords": ["true positive", "false positive", "incident", "endpoint", "email", "identity", "triage"],
                "priority": 2,
            },
            {
                "text": "Analyzed email-header components (SPF, DKIM, DMARC), sandboxed payloads and verified IOC reputations to mitigate phishing and business email compromise.",
                "keywords": ["phishing", "bec", "spf", "dkim", "dmarc", "ioc", "email", "sandbox"],
                "priority": 3,
            },
            {
                "text": "Executed rapid first-response containment including network isolation of compromised hosts, file quarantines and active session revocations.",
                "keywords": ["containment", "isolation", "quarantine", "incident response", "session revocation"],
                "priority": 4,
            },
            {
                "text": "Drafted clear 5W (Who, What, Where, When, Why) investigation reports strictly adhering to client SLAs and corporate SOPs.",
                "keywords": ["documentation", "sla", "sop", "5w", "investigation report", "reporting"],
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
        "name": "Active Directory Home Lab",
        "url": None,  # no public URL — rendered as plain text
        "subtitle": ": Windows Domain Administration",
        "bullets": [
            {
                "text": "Deployed Windows Server 2016 on VirtualBox as an Active Directory (AD DS) domain controller, with DNS lookup zones and OUs for user and group management.",
                "keywords": ["active directory", "windows server", "dns", "virtualbox", "domain controller", "ou"],
            },
            {
                "text": "Applied Group Policy for password and account-lockout policies, and delegated password-reset rights on OUs to non-admin users (least-privilege access).",
                "keywords": ["group policy", "password policy", "delegation", "least privilege", "active directory"],
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
    "degree": "Bachelor of Engineering (Cybersecurity, IoT and Blockchain Technology)",
    "university": "Osmania University",
    "dates": "Nov 2022 – May 2026",
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
# the same security work you performed.
ACCEPTABLE_ROLE_TITLES = [
    "SOC Analyst",
    "Security Operations Analyst",
    "Cybersecurity Analyst",
    "Security Analyst",
    "Threat Analyst",
    "Incident Response Analyst",
    "Blue Team Analyst",
    "IAM Analyst",
    "Identity Analyst",
    "Identity & Access Management Analyst",
    "Access Management Analyst",
]
