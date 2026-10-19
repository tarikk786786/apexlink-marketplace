"""
Template Management & Categorization Engine
Loads and categorizes backlink submission endpoints from curated seeds and upstream databases.
Prioritizes Tier 1 & Tier 2 verified high-authority endpoints (DA 70 - 99).
"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# Verified High-Authority Built-in Endpoints (DA 70 - 99)
CURATED_SEEDS = [
    # Tier 1: Search Engine Pingers & Crawlers (DA 95-99)
    {"url": "https://www.google.com/ping?sitemap=[ENCODE_URL]", "category": "search_ping", "da": 99, "tier": "Tier 1"},
    {"url": "https://www.bing.com/ping?sitemap=[ENCODE_URL]", "category": "search_ping", "da": 96, "tier": "Tier 1"},
    {"url": "https://rpc.pingomatic.com/?title=[ENCODE_DOMAIN]&blogurl=[ENCODE_URL]", "category": "search_ping", "da": 88, "tier": "Tier 1"},
    {"url": "https://feedburner.google.com/fb/a/pingSubmit?blogUrl=[ENCODE_URL]", "category": "search_ping", "da": 98, "tier": "Tier 1"},
    
    # Tier 1: Web Archives & Permanent Snapshots (DA 88-96)
    {"url": "https://web.archive.org/save/[URL]", "category": "archive", "da": 96, "tier": "Tier 1"},
    {"url": "https://archive.today/?run=1&url=[ENCODE_URL]", "category": "archive", "da": 89, "tier": "Tier 1"},
    {"url": "https://archive.is/?run=1&url=[ENCODE_URL]", "category": "archive", "da": 89, "tier": "Tier 1"},
    {"url": "https://archive.ph/?run=1&url=[ENCODE_URL]", "category": "archive", "da": 88, "tier": "Tier 1"},
    
    # Tier 1: Web Standards & Security Authorities (DA 89-98)
    {"url": "https://validator.w3.org/nu/?doc=[ENCODE_URL]", "category": "analytics", "da": 98, "tier": "Tier 1"},
    {"url": "https://validator.w3.org/mobile/check?docAddr=[ENCODE_URL]", "category": "analytics", "da": 98, "tier": "Tier 1"},
    {"url": "https://transparencyreport.google.com/safe-browsing/search?url=[ENCODE_URL]", "category": "analytics", "da": 99, "tier": "Tier 1"},
    {"url": "https://sitecheck.sucuri.net/results/{{DOMAIN}}", "category": "analytics", "da": 89, "tier": "Tier 1"},
    {"url": "https://safeweb.norton.com/report/show?url={{DOMAIN}}", "category": "analytics", "da": 92, "tier": "Tier 1"},
    {"url": "https://www.ssllabs.com/ssltest/analyze.html?d={{DOMAIN}}", "category": "analytics", "da": 91, "tier": "Tier 1"},

    # Tier 1 & 2: SEO Audits & Analytics Checkers (DA 75-92)
    {"url": "https://builtwith.com/{{DOMAIN}}", "category": "analytics", "da": 89, "tier": "Tier 1"},
    {"url": "https://www.similarweb.com/website/{{DOMAIN}}", "category": "analytics", "da": 91, "tier": "Tier 1"},
    {"url": "https://www.woorank.com/en/teaser-review/{{DOMAIN}}", "category": "analytics", "da": 87, "tier": "Tier 1"},
    {"url": "https://sitechecker.pro/seo-report/{{DOMAIN}}", "category": "analytics", "da": 79, "tier": "Tier 2"},
    {"url": "https://webseiten-analyse24.de/en/www/{{DOMAIN}}", "category": "analytics", "da": 72, "tier": "Tier 2"},
    {"url": "https://website.ip-adress.com/{{DOMAIN}}", "category": "analytics", "da": 74, "tier": "Tier 2"},
    {"url": "https://altovalleit.com/tools/robots-txt-tester/{{DOMAIN}}", "category": "analytics", "da": 68, "tier": "Tier 2"},
    {"url": "https://urlvoid.com/scan/{{DOMAIN}}/", "category": "analytics", "da": 75, "tier": "Tier 2"},
    
    # Tier 1 & 2: Whois & DNS Authorities (DA 71-88)
    {"url": "https://whois.domaintools.com/{{DOMAIN}}", "category": "whois", "da": 88, "tier": "Tier 1"},
    {"url": "https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{{DOMAIN}}", "category": "whois", "da": 86, "tier": "Tier 1"},
    {"url": "https://securitytrails.com/domain/{{DOMAIN}}/dns", "category": "whois", "da": 82, "tier": "Tier 2"},
    {"url": "https://viewdns.info/whois/?domain={{DOMAIN}}", "category": "whois", "da": 74, "tier": "Tier 2"},
    {"url": "https://www.robtex.com/dns-lookup/{{DOMAIN}}", "category": "whois", "da": 78, "tier": "Tier 2"},
    {"url": "https://intodns.com/{{DOMAIN}}", "category": "whois", "da": 71, "tier": "Tier 2"},
    
    # Tier 1 & 2: Search Engine Site Indexers & Reputable Directories (DA 70-98)
    {"url": "https://scholar.google.com/scholar?q=site:{{DOMAIN}}", "category": "directory", "da": 99, "tier": "Tier 1"},
    {"url": "https://html.duckduckgo.com/html/?q=site:{{DOMAIN}}", "category": "directory", "da": 92, "tier": "Tier 1"},
    {"url": "https://search.yahoo.com/search?p=site:{{DOMAIN}}", "category": "directory", "da": 95, "tier": "Tier 1"},
    {"url": "https://www.webwiki.com/{{DOMAIN}}", "category": "directory", "da": 76, "tier": "Tier 2"},
    {"url": "https://aboutus.com/{{DOMAIN}}", "category": "directory", "da": 77, "tier": "Tier 2"},
    {"url": "https://forums2.battleon.com/f/interceptor.asp?dest={{NOPROTOCOL_URL}}/", "category": "directory", "da": 70, "tier": "Tier 2"},
    {"url": "https://www.zapmeta.com/ws?q=site:{{DOMAIN}}", "category": "directory", "da": 73, "tier": "Tier 2"}
]

UPSTREAM_TEMPLATES_URL = "https://backlink-generator-tool.github.io/backlink-generator-tool/backlink-templates.json"
UPSTREAM_YOUTUBE_URL = "https://backlink-generator-tool.github.io/backlink-generator-tool/youtube-backlink-templates.json"

CACHE_DIR = Path(__file__).resolve().parent.parent / "data"
TEMPLATES_CACHE_FILE = CACHE_DIR / "backlink-templates.json"
YOUTUBE_CACHE_FILE = CACHE_DIR / "youtube-backlink-templates.json"


def categorize_url(endpoint: str) -> str:
    """Classifies an endpoint URL into an operational category."""
    ep = endpoint.lower()
    if any(k in ep for k in ["archive.org", "archive.today", "archive.is", "archive.ph", "archive.md"]):
        return "archive"
    if any(k in ep for k in ["google.com/ping", "bing.com/ping", "pingomatic", "rpc", "feedburner"]):
        return "search_ping"
    if any(k in ep for k in ["whois", "dns", "robtex", "mxtoolbox", "securitytrails", "intodns"]):
        return "whois"
    if any(k in ep for k in ["woorank", "similarweb", "stat", "analyse", "audit", "report", "ip-adress", "alexa", "builtwith", "validator.w3.org", "sucuri", "norton", "ssllabs", "urlvoid"]):
        return "analytics"
    if any(k in ep for k in ["video", "youtube", "watch", "ultra-zone", "embed"]):
        return "video_embed"
    return "directory"


class TemplateRepository:
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._templates: List[Dict[str, str]] = []
        self._youtube_templates: List[Dict[str, str]] = []
        self._loaded = False

    def load(self, force_refresh: bool = False) -> None:
        if self._loaded and not force_refresh:
            return

        # Start with curated Tier 1 seeds first
        curated_urls = [s["url"] for s in CURATED_SEEDS]
        loaded_general = list(curated_urls)

        # Load standard templates
        if not TEMPLATES_CACHE_FILE.exists() or force_refresh:
            try:
                req = urllib.request.Request(UPSTREAM_TEMPLATES_URL, headers={"User-Agent": "ApexLinkStudio/2.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    remote_data = json.loads(resp.read().decode("utf-8"))
                    with open(TEMPLATES_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(remote_data, f)
                    loaded_general.extend(remote_data)
            except Exception:
                pass
        else:
            try:
                with open(TEMPLATES_CACHE_FILE, "r", encoding="utf-8") as f:
                    loaded_general.extend(json.load(f))
            except Exception:
                pass

        # Load YouTube templates
        loaded_youtube: List[str] = []
        if not YOUTUBE_CACHE_FILE.exists() or force_refresh:
            try:
                req = urllib.request.Request(UPSTREAM_YOUTUBE_URL, headers={"User-Agent": "ApexLinkStudio/2.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    remote_yt = json.loads(resp.read().decode("utf-8"))
                    with open(YOUTUBE_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(remote_yt, f)
                    loaded_youtube.extend(remote_yt)
            except Exception:
                pass
        else:
            try:
                with open(YOUTUBE_CACHE_FILE, "r", encoding="utf-8") as f:
                    loaded_youtube.extend(json.load(f))
            except Exception:
                pass

        # Deduplicate while preserving order (curated high-authority first)
        seen = set()
        self._templates = []
        for u in loaded_general:
            clean = u.strip()
            if clean and clean not in seen:
                seen.add(clean)
                cat = categorize_url(clean)
                self._templates.append({"url": clean, "category": cat})

        yt_seen = set()
        self._youtube_templates = []
        for u in loaded_youtube:
            clean = u.strip()
            if clean and clean not in yt_seen:
                yt_seen.add(clean)
                self._youtube_templates.append({"url": clean, "category": "video_embed"})

        self._loaded = True

    def get_templates(self, is_youtube: bool = False, category: Optional[str] = None, high_quality_only: bool = False) -> List[Dict[str, str]]:
        self.load()
        source = self._youtube_templates if is_youtube else self._templates
        
        results = []
        for item in source:
            cat = item["category"]
            if category and category != "all" and cat != category:
                continue
            results.append(item)
            
        return results

    @property
    def total_count(self) -> int:
        self.load()
        return len(self._templates)


# Global singleton
repo = TemplateRepository()
