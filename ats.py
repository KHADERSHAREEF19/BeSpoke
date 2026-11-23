# ============================================================
# ats.py
# Weighted ATS-style keyword matcher for UAE security job ads.
#
# Method (deterministic, runs fully offline — no external API):
#   1. Scan the JD for a curated dictionary of security-domain
#      concepts (tools, techniques, certs, soft skills).
#   2. Each concept carries a weight (core skills weigh more) and
#      earns a small bonus for being repeated in the JD.
#   3. Match concepts against the resume text with word-boundary
#      rules, abbreviation/synonym expansion and plural handling.
#   4. Score = weighted coverage = matched weight / total JD weight.
#
# It is a keyword-coverage estimate, not a secret vendor algorithm.
# ============================================================

import re

# (canonical name, [variants...], category, weight)
CONCEPTS = [
    # --- Security operations core -------------------------------------
    ("SOC operations", ["soc", "security operations center", "security operations centre",
                        "security operations"], "Security Operations", 2),
    ("SIEM", ["siem", "security information and event management",
              "security information & event management", "sim"], "SIEM & Monitoring", 2),
    ("alert triage", ["alert triage", "triage", "alert handling", "alert investigation"],
     "Security Operations", 2),
    ("incident response", ["incident response", "incident handling", "ir"],
     "Security Operations", 2),
    ("incident management", ["incident management", "incident lifecycle",
                             "incident coordination"], "Security Operations", 2),
    ("security monitoring", ["security monitoring", "monitoring", "soc monitoring"],
     "SIEM & Monitoring", 2),
    ("threat detection", ["threat detection", "detection engineering",
                          "detection and response"], "Security Operations", 2),
    ("threat hunting", ["threat hunting", "proactive hunting", "threat hunt"],
     "Security Operations", 2),
    ("threat intelligence", ["threat intelligence", "cyber threat intelligence",
                             "cti", "threat intel"], "Threat Intelligence", 2),
    ("log analysis", ["log analysis", "log review", "log monitoring",
                      "logs analysis", "event analysis"], "SIEM & Monitoring", 2),
    ("phishing analysis", ["phishing", "phishing analysis", "email phishing"],
     "Email Security", 2),
    ("business email compromise", ["business email compromise", "bec"],
     "Email Security", 2),
    ("email security", ["email security", "email protection", "mail security"],
     "Email Security", 1),
    ("SPF/DKIM/DMARC", ["spf", "dkim", "dmarc", "email authentication"],
     "Email Security", 1),
    ("malware analysis", ["malware", "malware analysis", "malicious file",
                          "ransomware", "trojan", "virus"], "Security Operations", 2),
    ("digital forensics", ["forensic", "forensics", "digital forensics",
                           "dfir", "computer forensics"], "Forensics", 2),
    ("incident containment", ["containment", "first response", "initial response",
                              "quarantine", "isolation"], "Security Operations", 2),
    ("remediation", ["remediation", "remediate", "mitigation"], "Security Operations", 1),
    ("escalation", ["escalation", "escalate", "escalations"], "Security Operations", 1),
    ("post-incident review", ["postmortem", "post-mortem", "post incident",
                              "post-incident", "root cause", "lessons learned"],
     "Security Operations", 1),
    ("runbooks / playbooks", ["runbook", "runbooks", "playbook", "playbooks",
                              "standard operating procedure", "sop", "sops"],
     "Security Operations", 1),
    ("shift / on-call work", ["shift", "shifts", "on-call", "on call", "24/7",
                              "24x7", "night shift", "rotational shift"],
     "Ways of Working", 1),

    # --- SIEM / monitoring platforms ----------------------------------
    ("Microsoft Sentinel", ["microsoft sentinel", "azure sentinel", "sentinel"],
     "SIEM & Monitoring", 3),
    ("Splunk", ["splunk", "splunk enterprise"], "SIEM & Monitoring", 3),
    ("IBM QRadar", ["qradar", "ibm qradar"], "SIEM & Monitoring", 2),
    ("ArcSight", ["arcsight", "micro focus arcsight", "hp arcsight"],
     "SIEM & Monitoring", 2),
    ("LogRhythm", ["logrhythm"], "SIEM & Monitoring", 2),
    ("RSA NetWitness", ["rsa netwitness", "netwitness", "rsa security"],
     "SIEM & Monitoring", 2),
    ("Wazuh", ["wazuh"], "SIEM & Monitoring", 1),
    ("Exabeam", ["exabeam"], "SIEM & Monitoring", 1),
    ("Elastic SIEM", ["elastic siem", "elasticsearch siem", "elk siem"],
     "SIEM & Monitoring", 1),
    ("KQL", ["kql", "kusto", "kusto query language"], "SIEM & Monitoring", 1),
    ("SOAR", ["soar", "security orchestration", "orchestration and automation"],
     "SIEM & Monitoring", 2),
    ("UEBA", ["ueba", "user and entity behavior analytics",
              "user behaviour analytics"], "SIEM & Monitoring", 1),

    # --- Endpoint / network detection ----------------------------------
    ("EDR", ["edr", "endpoint detection and response"], "Detection & Response", 2),
    ("XDR", ["xdr", "extended detection and response"], "Detection & Response", 2),
    ("Microsoft Defender XDR", ["defender xdr", "microsoft defender", "mde",
                                "mdo", "mdi", "mdca", "defender for endpoint"],
     "Detection & Response", 2),
    ("CrowdStrike", ["crowdstrike", "crowdstrike falcon", "falcon"], "Detection & Response", 2),
    ("Carbon Black", ["carbon black", "vmware carbon black"], "Detection & Response", 1),
    ("Tanium", ["tanium"], "Detection & Response", 1),
    ("antivirus", ["antivirus", "anti-virus", "endpoint protection",
                   "endpoint security"], "Detection & Response", 1),
    ("IDS/IPS", ["ids", "ips", "intrusion detection", "intrusion prevention"],
     "Network & Perimeter", 2),
    ("network traffic analysis", ["network traffic", "traffic analysis",
                                  "packet analysis", "packet capture", "pcap"],
     "Network & Perimeter", 2),
    ("Wireshark", ["wireshark"], "Network & Perimeter", 1),
    ("Nmap", ["nmap", "network scanning", "port scanning"], "Network & Perimeter", 1),
    ("vulnerability assessment", ["vulnerability assessment", "vulnerability management",
                                  "vulnerability scanning", "vulnerabilities"],
     "Vulnerability Management", 2),
    ("penetration testing", ["penetration testing", "pen testing", "pentest",
                             "ethical hacking", "red team"], "Vulnerability Management", 2),
    ("Nessus", ["nessus"], "Vulnerability Management", 1),
    ("Qualys", ["qualys"], "Vulnerability Management", 1),
    ("Metasploit", ["metasploit"], "Vulnerability Management", 1),
    ("Burp Suite", ["burp suite", "burpsuite", "owasp"], "Vulnerability Management", 1),
    ("patch management", ["patch management", "patching", "security patches",
                          "patch deployment"], "Vulnerability Management", 1),
    ("MITRE ATT&CK", ["mitre", "att&ck", "att&ck framework", "ttps"],
     "Threat Intelligence", 1),
    ("IOC handling", ["ioc", "iocs", "indicator of compromise", "indicators of compromise"],
     "Threat Intelligence", 1),
    ("OSINT", ["osint", "open source intelligence"], "Threat Intelligence", 1),
    ("VirusTotal", ["virustotal"], "Threat Intelligence", 1),
    ("AbuseIPDB", ["abuseipdb"], "Threat Intelligence", 1),
    ("sandbox analysis", ["sandbox", "sandboxing"], "Threat Intelligence", 1),
    ("reverse engineering", ["reverse engineering", "malware reverse"],
     "Forensics", 1),
    ("memory forensics", ["memory forensics", "volatility"], "Forensics", 1),

    # --- IAM ----------------------------------------------------------
    ("identity & access management", ["iam", "identity and access management",
                                      "identity & access management", "identity management",
                                      "access management"], "IAM & Access", 3),
    ("PingOne", ["pingone", "ping identity", "pingone workforce", "ping"],
     "IAM & Access", 2),
    ("Okta", ["okta"], "IAM & Access", 2),
    ("Saviynt", ["saviynt"], "IAM & Access", 1),
    ("Sailpoint", ["sailpoint"], "IAM & Access", 1),
    ("CyberArk", ["cyberark"], "IAM & Access", 2),
    ("BeyondTrust", ["beyondtrust"], "IAM & Access", 1),
    ("privileged access management", ["privileged access management", "pam",
                                      "privileged access"], "IAM & Access", 2),
    ("SSO", ["sso", "single sign-on", "single sign on"], "IAM & Access", 2),
    ("MFA", ["mfa", "multi-factor authentication", "multifactor authentication",
             "multi factor authentication", "2fa", "two-factor"],
     "IAM & Access", 2),
    ("SAML", ["saml", "saml 2.0"], "IAM & Access", 1),
    ("OIDC", ["oidc", "openid connect", "open id connect"], "IAM & Access", 1),
    ("OAuth", ["oauth", "oauth 2.0"], "IAM & Access", 1),
    ("RBAC", ["rbac", "role-based access control", "role based access control"],
     "IAM & Access", 1),
    ("CIAM", ["ciam", "customer iam", "customer identity"], "IAM & Access", 1),
    ("Entra ID", ["entra id", "microsoft entra", "azure ad", "azure active directory",
                  "entra"], "IAM & Access", 2),
    ("Active Directory", ["active directory", "ad ds", "adds", "domain controller",
                          "group policy"], "IAM & Access", 2),
    ("LDAP", ["ldap"], "IAM & Access", 1),
    ("identity proofing / KYC", ["identity proofing", "identity verification",
                                "kyc", "selfie verification"], "IAM & Access", 1),

    # --- Network & perimeter -------------------------------------------
    ("firewall management", ["firewall", "firewalls", "next-generation firewall",
                             "ngfw"], "Network & Perimeter", 2),
    ("Fortinet FortiGate", ["fortigate", "fortinet", "forti"], "Network & Perimeter", 1),
    ("Palo Alto", ["palo alto", "palo alto networks"], "Network & Perimeter", 1),
    ("Cisco networking", ["cisco", "ccna", "ccnp", "cisco ios"], "Network & Perimeter", 1),
    ("TCP/IP", ["tcp/ip", "tcp ip", "transmission control protocol"], "Network & Perimeter", 1),
    ("DNS", ["dns", "domain name system"], "Network & Perimeter", 1),
    ("DHCP", ["dhcp"], "Network & Perimeter", 1),
    ("VPN", ["vpn", "virtual private network", "remote access"], "Network & Perimeter", 1),
    ("proxy / web filtering", ["proxy", "web filtering", "secure web gateway",
                              "swg", "zscaler"], "Network & Perimeter", 1),
    ("DLP", ["dlp", "data loss prevention"], "Network & Perimeter", 1),
    ("network segmentation", ["network segmentation", "segmentation",
                              "microsegmentation"], "Network & Perimeter", 1),
    ("WAN/LAN", ["wan", "lan", "routing", "switching"], "Network & Perimeter", 1),
    ("Wi-Fi security", ["wi-fi", "wifi", "wireless security", "wlan"], "Network & Perimeter", 1),

    # --- Cloud & infrastructure ---------------------------------------
    ("cloud security", ["cloud security", "cloud", "casb", "cloud-native"],
     "Cloud & Infrastructure", 2),
    ("AWS", ["aws", "amazon web services"], "Cloud & Infrastructure", 2),
    ("Microsoft Azure", ["azure", "microsoft azure"], "Cloud & Infrastructure", 2),
    ("Google Cloud", ["gcp", "google cloud"], "Cloud & Infrastructure", 1),
    ("Microsoft 365", ["office 365", "microsoft 365", "m365", "o365"],
     "Cloud & Infrastructure", 1),
    ("Linux administration", ["linux", "ubuntu", "centos", "rhel", "red hat"],
     "Cloud & Infrastructure", 2),
    ("Windows Server", ["windows server", "server 2019", "server 2022",
                        "windows administration"], "Cloud & Infrastructure", 2),
    ("Virtualization", ["virtualization", "virtualisation", "vmware", "virtualbox",
                        "hyper-v"], "Cloud & Infrastructure", 1),
    ("Docker", ["docker", "containers", "containerization"], "DevOps & Automation", 1),
    ("Kubernetes", ["kubernetes", "k8s"], "DevOps & Automation", 1),
    ("Infrastructure as Code", ["terraform", "ansible", "infrastructure as code",
                                "iac"], "DevOps & Automation", 1),

    # --- Scripting & automation ---------------------------------------
    ("Python", ["python"], "DevOps & Automation", 2),
    ("PowerShell", ["powershell"], "DevOps & Automation", 2),
    ("Bash / shell scripting", ["bash", "shell scripting", "shell script",
                                "scripting"], "DevOps & Automation", 2),
    ("SQL", ["sql", "mysql", "postgresql", "t-sql", "pl/sql"], "DevOps & Automation", 1),
    ("Git", ["git", "github", "gitlab", "version control"], "DevOps & Automation", 1),
    ("automation", ["automation", "automate", "automated workflows", "n8n"],
     "DevOps & Automation", 1),
    ("API integration", ["api", "rest api", "apis", "webhooks"], "DevOps & Automation", 1),

    # --- Governance, risk & compliance --------------------------------
    ("ISO 27001", ["iso 27001", "iso27001", "iso 27001:2022", "iso/iec 27001"],
     "Governance & Compliance", 2),
    ("NIST", ["nist", "nist csf", "nist framework", "nist 800"], "Governance & Compliance", 2),
    ("PCI DSS", ["pci dss", "pci-dss", "pci compliance"], "Governance & Compliance", 2),
    ("GDPR", ["gdpr", "general data protection regulation", "data protection"],
     "Governance & Compliance", 2),
    ("SOC 2", ["soc 2", "soc2", "soc ii"], "Governance & Compliance", 1),
    ("risk assessment", ["risk assessment", "risk analysis", "risk management",
                         "risk register"], "Governance & Compliance", 2),
    ("compliance", ["compliance", "regulatory", "regulations"], "Governance & Compliance", 2),
    ("audit", ["audit", "auditing", "internal audit", "external audit"],
     "Governance & Compliance", 1),
    ("security policies", ["security policy", "security policies", "policy",
                           "standards", "frameworks", "guidelines"],
     "Governance & Compliance", 1),
    ("business continuity", ["business continuity", "bcp", "disaster recovery", "dr"],
     "Governance & Compliance", 1),

    # --- Certs ---------------------------------------------------------
    ("CISSP", ["cissp"], "Certifications", 2),
    ("CEH", ["ceh", "certified ethical hacker"], "Certifications", 2),
    ("OSCP", ["oscp", "offensive security"], "Certifications", 1),
    ("CompTIA Security+", ["comptia security+", "security+", "security plus"],
     "Certifications", 2),
    ("CompTIA Network+", ["comptia network+", "network+", "network plus"],
     "Certifications", 1),
    ("CCNA", ["ccna"], "Certifications", 1),
    ("CISA", ["cisa"], "Certifications", 1),
    ("CISM", ["cism"], "Certifications", 1),
    ("ISC2 CC", ["isc2 cc", "certified in cybersecurity", "cc certification"],
     "Certifications", 1),
    ("ITIL", ["itil"], "Certifications", 1),
    ("cloud certifications", ["aws certified", "azure fundamentals", "az-900",
                              "cloud certification"], "Certifications", 1),

    # --- Ways of working / soft skills --------------------------------
    ("documentation & reporting", ["documentation", "documenting", "report writing",
                                   "reporting", "reports", "dashboards"],
     "Ways of Working", 2),
    ("communication skills", ["communication", "communicate", "written and verbal",
                              "presentation"], "Soft Skills", 2),
    ("stakeholder management", ["stakeholder", "stakeholders", "customer facing",
                                "client facing", "liaise", "liaison"],
     "Soft Skills", 1),
    ("team collaboration", ["teamwork", "team player", "collaboration",
                            "collaborate", "cross-functional"], "Soft Skills", 1),
    ("problem solving", ["problem solving", "problem-solving", "analytical",
                         "troubleshooting", "troubleshoot"], "Soft Skills", 1),
    ("time management", ["time management", "prioritize", "prioritise",
                         "multitask", "deadline"], "Soft Skills", 1),
    ("attention to detail", ["attention to detail", "detail-oriented",
                             "accuracy"], "Soft Skills", 1),
    ("mentoring / leadership", ["mentoring", "mentor", "leadership", "led",
                                "supervised", "training", "coach"], "Soft Skills", 1),
    ("ticketing systems", ["ticketing", "service now", "servicenow", "jira",
                           "remedy", "freshservice"], "Ways of Working", 1),
    ("SLA awareness", ["sla", "slas", "service level agreement"], "Ways of Working", 1),
]

# Concept variants that are too generic to trust on their own.
_STOPWORDS = {
    "and", "or", "the", "of", "for", "to", "in", "on", "with", "you", "your",
}


def _matches(variant, text):
    """Word-boundary match with plural tolerance for short tokens."""
    variant = variant.lower().strip()
    if not variant or variant in _STOPWORDS:
        return []
    if len(variant) <= 4:
        pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"s?(?![a-z0-9])"
    else:
        pattern = r"(?<![a-z0-9])" + re.escape(variant)
    return re.findall(pattern, text)


def normalize_text(*parts):
    return " ".join(str(p) for p in parts if p).lower()


def auto_keywords(text):
    """Tag free-text content (uploaded resumes have no keyword lists)."""
    hits = []
    for canonical, variants, _category, _weight in CONCEPTS:
        if any(_matches(variant, text) for variant in variants):
            hits.append(canonical.lower())
    return hits


def resume_search_text(profile):
    """All visible resume content, lowercased, for matching."""
    personal = profile.get("PERSONAL", {})
    bits = [
        personal.get("name", ""), personal.get("role_label", ""),
        profile.get("SUMMARY_TEMPLATE", ""), profile.get("CERT_LINE", ""),
    ]
    for job in profile.get("EXPERIENCE", []):
        bits += [job.get("title", ""), job.get("company", "")]
        bits += [b.get("text", "") for b in job.get("bullets", [])]
    for project in profile.get("PROJECTS", []):
        bits += [project.get("name", ""), project.get("subtitle", "")]
        bits += [b.get("text", "") for b in project.get("bullets", [])]
    for category, skill_list in profile.get("SKILLS", {}).items():
        bits.append(category)
        bits += [s.get("skill", "") for s in skill_list]
    for cert in profile.get("CERTIFICATIONS", []):
        bits.append(cert.get("name", ""))
    bits += profile.get("ACHIEVEMENTS", [])
    return normalize_text(*bits)


_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:years|yrs|year)", re.I)


def extract_experience_requirement(jd_text):
    """Highest 'N+ years' figure the JD asks for, if any."""
    hits = [int(n) for n in _YEARS_RE.findall(jd_text)]
    return max(hits) if hits else None


def score(jd_text, profile):
    """Return a weighted coverage report for this JD against the profile."""
    jd = jd_text.lower()
    resume_text = resume_search_text(profile)

    concepts = []
    matched_weight = 0.0
    total_weight = 0.0

    for canonical, variants, category, weight in CONCEPTS:
        count = sum(len(_matches(v, jd)) for v in variants)
        if count == 0:
            continue
        effective = weight * (1.0 + 0.25 * min(count - 1, 2))
        hit_variants = [v for v in variants if _matches(v, resume_text)]
        matched = bool(hit_variants)
        total_weight += effective
        if matched:
            matched_weight += effective
        concepts.append({
            "name": canonical,
            "category": category,
            "weight": round(effective, 2),
            "count": count,
            "matched": matched,
        })

    score_pct = round(matched_weight / total_weight * 100) if total_weight else 0

    by_category = {}
    for concept in concepts:
        bucket = by_category.setdefault(concept["category"], {"matched": 0, "total": 0})
        bucket["total"] += 1
        bucket["matched"] += 1 if concept["matched"] else 0

    return {
        "score": score_pct,
        "total_weight": round(total_weight, 2),
        "matched_weight": round(matched_weight, 2),
        "concept_count": len(concepts),
        "matched_count": sum(1 for c in concepts if c["matched"]),
        "matched": [c for c in concepts if c["matched"]],
        "missing": [c for c in concepts if not c["matched"]],
        "by_category": by_category,
        "years_required": extract_experience_requirement(jd_text),
    }
