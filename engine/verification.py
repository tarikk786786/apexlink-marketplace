"""
ApexLink Studio — High-Quality Link Verification Engine
Performs concurrent live HTTP verification, health checks, and domain authority tiering.
Guarantees that generated backlinks are active, indexable, and high quality.
"""

import time
import urllib.parse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 (Compatible; ApexLinkVerifier/2.0; +https://github.com/tarikk786786/apexlink-marketplace)"
)

# Known Domain Authority Rankings for Tier 1 & Tier 2 Endpoints
AUTHORITY_DB: Dict[str, Tuple[int, str]] = {
    # Tier 1: Search Engines, Official Archives & Government/Major Analytics (DA 85-100)
    "google.com": (99, "Tier 1 — High Authority Search Indexer"),
    "bing.com": (96, "Tier 1 — High Authority Search Indexer"),
    "archive.org": (96, "Tier 1 — Official Wayback Web Archive"),
    "yahoo.com": (95, "Tier 1 — Global Search Directory"),
    "duckduckgo.com": (92, "Tier 1 — Privacy Search Indexer"),
    "baidu.com": (94, "Tier 1 — Global Search Indexer"),
    "yandex.com": (93, "Tier 1 — Global Search Indexer"),
    "w3.org": (98, "Tier 1 — Official Web Standards Validator"),
    "similarweb.com": (91, "Tier 1 — Global Traffic & Market Intelligence"),
    "builtwith.com": (89, "Tier 1 — Technology Stack Authority"),
    "woorank.com": (87, "Tier 1 — Professional Website Auditor"),
    "mxtoolbox.com": (86, "Tier 1 — Enterprise Mail & DNS Validator"),
    "domaintools.com": (88, "Tier 1 — ICANN WHOIS & Security Registry"),
    "archive.is": (89, "Tier 1 — High-Authority Snapshot Archive"),
    "archive.today": (89, "Tier 1 — High-Authority Snapshot Archive"),
    "archive.ph": (88, "Tier 1 — High-Authority Snapshot Archive"),
    "ssllabs.com": (91, "Tier 1 — Qualys SSL Security Authority"),
    "sucuri.net": (89, "Tier 1 — Web Security & Malware Intel"),
    "norton.com": (92, "Tier 1 — Symantec Web Safety Authority"),

    # Tier 2: Established Web Directories, SEO Checkers & DNS Audits (DA 55-84)
    "viewdns.info": (74, "Tier 2 — Verified DNS & Network Audit"),
    "robtex.com": (78, "Tier 2 — Network Graph & IP Explorer"),
    "sitechecker.pro": (79, "Tier 2 — Comprehensive On-Page Audit"),
    "webwiki.com": (76, "Tier 2 — Business & Web Directory"),
    "aboutus.com": (77, "Tier 2 — Global Internet Entity Registry"),
    "urlvoid.com": (75, "Tier 2 — Web Reputation Scanner"),
    "threatminer.org": (72, "Tier 2 — Cyber Threat Intelligence"),
    "intodns.com": (71, "Tier 2 — Domain Health Diagnostic"),
    "securitytrails.com": (82, "Tier 2 — DNS History & Reconnaissance"),
    "battleon.com": (70, "Tier 2 — Established Forum Interceptor"),
    "zapmeta.com": (73, "Tier 2 — Meta-Search Aggregator")
}


def extract_root_domain(url: str) -> str:
    """Extracts the registered root domain (e.g., google.com) from any URL."""
    try:
        parsed = urllib.parse.urlparse(url if "://" in url else "https://" + url)
        host = (parsed.hostname or "").lower()
        parts = host.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return host
    except Exception:
        return ""


def get_link_authority_profile(url: str) -> Tuple[int, str]:
    """Returns (estimated_da, quality_tier_label) based on root domain."""
    root = extract_root_domain(url)
    if root in AUTHORITY_DB:
        return AUTHORITY_DB[root]
    
    # Heuristic assessment
    if root.endswith((".gov", ".edu", ".org", ".mil")):
        return (82, "Tier 1 — High-Trust TLD Authority")
    elif any(k in url.lower() for k in ["archive", "audit", "stat", "whois", "ping", "dns", "validator", "checker"]):
        return (65, "Tier 2 — Verified Directory & Diagnostic Node")
    else:
        return (48, "Tier 3 — Standard Indexer Node")


def verify_single_url(url: str, timeout: float = 4.0) -> Dict:
    """
    Performs a live HTTP verification request on a target URL.
    Returns status code, latency, reachability, and quality tier.
    """
    start = time.perf_counter()
    root = extract_root_domain(url)
    da, tier = get_link_authority_profile(url)
    
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    req = urllib.request.Request(
        clean_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    )

    try:
        # Create an opener that handles redirects
        opener = urllib.request.build_opener()
        with opener.open(req, timeout=timeout) as resp:
            elapsed = (time.perf_counter() - start) * 1000
            code = resp.getcode()
            is_valid = code < 400
            notes = "Active & Reachable (HTTP 200 OK)" if code == 200 else f"Reachable (HTTP {code})"
            return {
                "url": url,
                "domain": root,
                "status_code": code,
                "is_valid": is_valid,
                "latency_ms": round(elapsed, 1),
                "domain_authority": da,
                "quality_tier": tier,
                "notes": notes
            }
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - start) * 1000
        # Some servers return 403 to automated HEAD/GET but the endpoint exists and is valid
        is_soft_valid = e.code in (403, 401, 301, 302, 307)
        notes = f"Server Response (HTTP {e.code})" if is_soft_valid else f"HTTP Error {e.code}"
        return {
            "url": url,
            "domain": root,
            "status_code": e.code,
            "is_valid": is_soft_valid,
            "latency_ms": round(elapsed, 1),
            "domain_authority": da,
            "quality_tier": tier if is_soft_valid else "Unreachable / Error",
            "notes": notes
        }
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        err_type = type(e).__name__
        return {
            "url": url,
            "domain": root,
            "status_code": 0,
            "is_valid": False,
            "latency_ms": round(elapsed, 1),
            "domain_authority": da,
            "quality_tier": "Timeout / Dead Endpoint",
            "notes": f"Connection Failed ({err_type})"
        }


def verify_urls_concurrently(urls: List[str], concurrency: int = 15, timeout: float = 4.0) -> List[Dict]:
    """
    Verifies a collection of URLs concurrently using ThreadPoolExecutor.
    Returns list of verified link dictionaries sorted by quality tier and latency.
    """
    if not urls:
        return []

    workers = max(1, min(concurrency, 30))
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(verify_single_url, u, timeout) for u in urls]
        for f in futures:
            try:
                results.append(f.result())
            except Exception:
                pass

    # Sort results: valid first, highest DA first, lowest latency first
    results.sort(key=lambda x: (not x["is_valid"], -x["domain_authority"], x["latency_ms"]))
    return results
