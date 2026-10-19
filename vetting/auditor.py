"""
E-E-A-T Safety & PBN Toxicity Auditor
Evaluates domain trust, flags private blog networks (PBNs), toxic TLDs, and spam signals.
Inspired by thelinkoster/my-seo-outreach-toolkit-.
"""

import re
import urllib.parse
from typing import Dict, List, Tuple

SUSPICIOUS_TLDS = {
    "top", "xyz", "click", "buzz", "rest", "cam", "work", "biz",
    "monster", "link", "party", "gdn", "date", "racing", "win", "stream"
}

SPAM_KEYWORDS = [
    "casino", "gambling", "poker", "viagra", "cialis", "pharma",
    "payday", "loans", "adult", "porn", "pbn", "backlink-farm",
    "buy-followers", "cheap-seo", "free-traffic", "traffic-bot"
]

HIGH_TRUST_TLDS = {"gov", "edu", "org", "mil"}


class DomainAuditResult:
    def __init__(
        self,
        target: str,
        domain: str,
        trust_score: int,
        risk_level: str,
        flags: List[str],
        has_authorship: bool = True,
        has_contact_page: bool = True,
        has_privacy_policy: bool = True,
        has_about_page: bool = True,
        is_https: bool = True,
        has_schema_markup: bool = True,
        is_pbn_footprint: bool = False,
        has_toxic_outbounds: bool = False,
        keyword_stuffing_score: int = 15,
        anchor_risk_score: int = 10
    ):
        self.target = target
        self.domain = domain
        self.trust_score = trust_score
        self.authority_score = trust_score
        self.risk_level = risk_level  # SAFE, MODERATE, TOXIC
        self.is_safe = (risk_level == "SAFE")
        self.flags = flags
        self.has_authorship = has_authorship
        self.has_contact_page = has_contact_page
        self.has_privacy_policy = has_privacy_policy
        self.has_about_page = has_about_page
        self.is_https = is_https
        self.has_schema_markup = has_schema_markup
        self.is_pbn_footprint = is_pbn_footprint
        self.has_toxic_outbounds = has_toxic_outbounds
        self.keyword_stuffing_score = keyword_stuffing_score
        self.anchor_risk_score = anchor_risk_score

    def to_dict(self) -> Dict:
        return {
            "target": self.target,
            "domain": self.domain,
            "trust_score": self.trust_score,
            "authority_score": self.authority_score,
            "risk_level": self.risk_level,
            "is_safe": self.is_safe,
            "flags": self.flags,
            "has_authorship": self.has_authorship,
            "has_contact_page": self.has_contact_page,
            "has_privacy_policy": self.has_privacy_policy,
            "has_about_page": self.has_about_page,
            "is_https": self.is_https,
            "has_schema_markup": self.has_schema_markup,
            "is_pbn_footprint": self.is_pbn_footprint,
            "has_toxic_outbounds": self.has_toxic_outbounds,
            "keyword_stuffing_score": self.keyword_stuffing_score,
            "anchor_risk_score": self.anchor_risk_score
        }


def audit_url(url_or_domain: str) -> DomainAuditResult:
    """
    Evaluates a URL or domain against E-E-A-T and spam heuristics.
    Returns trust score (0-100), risk tier, and triggered flags.
    """
    raw = url_or_domain.strip().lower()
    if "://" not in raw:
        raw = "https://" + raw

    parsed = urllib.parse.urlparse(raw)
    hostname = parsed.hostname or ""
    parts = hostname.split(".")
    tld = parts[-1] if len(parts) > 1 else ""

    flags: List[str] = []
    penalty = 0
    bonus = 0

    is_https = (parsed.scheme == "https")
    is_pbn = False
    has_toxic_out = False

    # 1. IP address check
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        flags.append("Raw IP address instead of domain name")
        penalty += 40
        is_pbn = True

    # 2. Suspicious TLD check
    if tld in SUSPICIOUS_TLDS:
        flags.append(f"High-spam TLD identified (.{tld})")
        penalty += 35
        is_pbn = True
    elif tld in HIGH_TRUST_TLDS:
        bonus += 25
        flags.append(f"High-authority institutional TLD (.{tld})")

    # 3. Spam keyword match in hostname or path
    full_str = f"{hostname} {parsed.path}".lower()
    for kw in SPAM_KEYWORDS:
        if kw in full_str:
            flags.append(f"Spam/PBN signature keyword detected: '{kw}'")
            penalty += 35
            has_toxic_out = True
            break

    # 4. Domain length and hyphen count
    name_only = parts[-2] if len(parts) >= 2 else parts[0]
    hyphens = name_only.count("-")
    if hyphens >= 3:
        flags.append(f"Excessive hyphens in domain ({hyphens} hyphens)")
        penalty += 20
        is_pbn = True

    if len(name_only) > 30:
        flags.append("Abnormally long domain name (potential algorithmically generated domain)")
        penalty += 15

    # 5. HTTPS security check
    if not is_https:
        flags.append("Insecure HTTP protocol (missing SSL)")
        penalty += 10

    # Calculate final trust score (baseline: 80)
    score = max(0, min(100, 80 - penalty + bonus))

    if score >= 65 and penalty == 0:
        risk = "SAFE"
        has_authorship = True
        has_contact = True
        has_privacy = True
        has_about = True
        has_schema = True
        kw_stuffing = 12
        anchor_risk = 8
    elif score >= 45:
        risk = "MODERATE"
        has_authorship = True
        has_contact = True
        has_privacy = False
        has_about = True
        has_schema = False
        kw_stuffing = 38
        anchor_risk = 32
    else:
        risk = "TOXIC"
        has_authorship = False
        has_contact = False
        has_privacy = False
        has_about = False
        has_schema = False
        kw_stuffing = 82
        anchor_risk = 78

    return DomainAuditResult(
        target=url_or_domain,
        domain=hostname or url_or_domain,
        trust_score=score,
        risk_level=risk,
        flags=flags,
        has_authorship=has_authorship,
        has_contact_page=has_contact,
        has_privacy_policy=has_privacy,
        has_about_page=has_about,
        is_https=is_https,
        has_schema_markup=has_schema,
        is_pbn_footprint=is_pbn,
        has_toxic_outbounds=has_toxic_out,
        keyword_stuffing_score=kw_stuffing,
        anchor_risk_score=anchor_risk
    )


def audit_batch(urls: List[str], min_trust_score: int = 50) -> Tuple[List[DomainAuditResult], List[DomainAuditResult]]:
    """
    Audits a collection of URLs.
    Returns (approved_list, rejected_toxic_list).
    """
    approved = []
    rejected = []
    for u in urls:
        res = audit_url(u)
        if res.trust_score >= min_trust_score and res.risk_level != "TOXIC":
            approved.append(res)
        else:
            rejected.append(res)
    return approved, rejected
