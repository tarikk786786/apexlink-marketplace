"""
Template Management & Categorization Engine
Loads and categorizes backlink submission endpoints from curated seeds and upstream databases.
"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# Core High-Authority Built-in Endpoints
CURATED_SEEDS = [
    # Search Engine Pingers
    {"url": "https://www.google.com/ping?sitemap=[ENCODE_URL]", "category": "search_ping"},
    {"url": "https://www.bing.com/ping?sitemap=[ENCODE_URL]", "category": "search_ping"},
    {"url": "https://rpc.pingomatic.com/?title=[ENCODE_DOMAIN]&blogurl=[ENCODE_URL]", "category": "search_ping"},
    
    # Web Archives & Snapshots
    {"url": "https://web.archive.org/save/[URL]", "category": "archive"},
    {"url": "https://archive.today/?run=1&url=[ENCODE_URL]", "category": "archive"},
    {"url": "https://archive.is/?run=1&url=[ENCODE_URL]", "category": "archive"},
    {"url": "https://archive.ph/?run=1&url=[ENCODE_URL]", "category": "archive"},
    
    # SEO Audits & Analytics Checkers
    {"url": "https://www.woorank.com/en/teaser-review/{{DOMAIN}}", "category": "analytics"},
    {"url": "https://webseiten-analyse24.de/en/www/{{DOMAIN}}", "category": "analytics"},
    {"url": "https://website.ip-adress.com/{{DOMAIN}}", "category": "analytics"},
    {"url": "https://altovalleit.com/tools/robots-txt-tester/{{DOMAIN}}", "category": "analytics"},
    {"url": "https://sitechecker.pro/seo-report/{{DOMAIN}}", "category": "analytics"},
    {"url": "https://www.similarweb.com/website/{{DOMAIN}}", "category": "analytics"},
    
    # Whois & DNS Lookups
    {"url": "https://whois.domaintools.com/{{DOMAIN}}", "category": "whois"},
    {"url": "https://viewdns.info/whois/?domain={{DOMAIN}}", "category": "whois"},
    {"url": "https://www.robtex.com/dns-lookup/{{DOMAIN}}", "category": "whois"},
    {"url": "https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{{DOMAIN}}", "category": "whois"},
    
    # Web Directories & Traffic Aggregators
    {"url": "https://forums2.battleon.com/f/interceptor.asp?dest={{NOPROTOCOL_URL}}/", "category": "directory"},
    {"url": "https://www.zapmeta.com/ws?q=site:{{DOMAIN}}", "category": "directory"},
    {"url": "https://scholar.google.com/scholar?q=site:{{DOMAIN}}", "category": "directory"}
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
    if any(k in ep for k in ["google.com/ping", "bing.com/ping", "pingomatic", "rpc"]):
        return "search_ping"
    if any(k in ep for k in ["whois", "dns", "robtex", "mxtoolbox"]):
        return "whois"
    if any(k in ep for k in ["woorank", "similarweb", "stat", "analyse", "audit", "report", "ip-adress", "alexa"]):
        return "analytics"
    if any(k in ep for k in ["video", "youtube", "watch", "ultra-zone", "embed"]):
        return "video_embed"
    return "directory"


class TemplateRepository:
    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._templates: List[str] = []
        self._youtube_templates: List[str] = []
        self._loaded = False

    def load(self, force_refresh: bool = False) -> None:
        if self._loaded and not force_refresh:
            return

        # Start with curated seeds
        base_urls = [s["url"] for s in CURATED_SEEDS]
        loaded_general = list(base_urls)

        # Load standard templates
        if not TEMPLATES_CACHE_FILE.exists() or force_refresh:
            try:
                req = urllib.request.Request(UPSTREAM_TEMPLATES_URL, headers={"User-Agent": "OmniLinkStudio/1.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    remote_data = json.loads(resp.read().decode("utf-8"))
                    with open(TEMPLATES_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(remote_data, f)
                    loaded_general.extend(remote_data)
            except Exception as e:
                # If offline, use built-in seeds
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
                req = urllib.request.Request(UPSTREAM_YOUTUBE_URL, headers={"User-Agent": "OmniLinkStudio/1.0"})
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

        # Deduplicate while preserving order
        seen = set()
        self._templates = []
        for u in loaded_general:
            clean = u.strip()
            if clean and clean not in seen:
                seen.add(clean)
                self._templates.append(clean)

        self._youtube_templates = list(dict.fromkeys(loaded_youtube))
        self._loaded = True

    def get_templates(self, is_youtube: bool = False, category: Optional[str] = None) -> List[Dict[str, str]]:
        self.load()
        source = self._youtube_templates if is_youtube else self._templates
        
        results = []
        for tpl in source:
            cat = categorize_url(tpl)
            if category and category != "all" and cat != category:
                continue
            results.append({"url": tpl, "category": cat})
        return results

    @property
    def total_count(self) -> int:
        self.load()
        return len(self._templates)


# Global singleton
repo = TemplateRepository()
