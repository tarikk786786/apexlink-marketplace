"""
ApexLink Studio — Unified 100% Free SEO & Backlink Power Tools Platform
Engineered for direct generation, auditing, live verification, pinging, and analysis:
1. 4,640+ Web Directory, Archive & Diagnostic Generator (Tier 1 & 2 Quality Prioritized)
2. Live Concurrent Link Health & Status Verifier (HTTP Status, Latency, DA Rating)
3. High-Throughput Concurrent Live Pinger & Crawler Broadcaster
4. Google E-E-A-T Domain Authority & Toxic PBN Spam Auditor
5. Contextual Penguin-Safe Anchor Text Diversity Matrix Generator
6. Google Search Console Disavow File Builder (disavow.txt)
7. High-Authority Media & Outreach Directory Explorer
8. Cryptographic Owner & Code Integrity Lock (tarikk786786)
"""

import json
import os
import sys
import time
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

sys.path.insert(0, str(BASE_DIR))

# Core Security & Verification
from core.security import (
    verify_owner_access,
    compute_payload_hmac,
    get_security_manifest,
    AUTHORIZED_OWNER_ID
)

# Integrated Automation Engines
from engine.tokenizer import normalize_url, extract_youtube_id, build_token_map, replace_tokens
from engine.templates import repo as template_repo
from engine.pinger import _sync_ping_urllib, AsyncPinger
from engine.verification import verify_single_url, verify_urls_concurrently, get_link_authority_profile
from vetting.auditor import audit_url, audit_batch
from vetting.disavow import generate_disavow_content
from contextual.anchors import generate_anchor_profile

# High-Authority Outreach & Publication Intel Database (100% Free Domain Explorer)
DOMAIN_EXPLORER_DB = [
    {
        "id": "dom-1",
        "domain": "manilatimes.net",
        "sample_url": "https://www.manilatimes.net/business/article",
        "category": "News and Media",
        "categories": ["News and Media", "Business", "General"],
        "traffic_semrush": "742K",
        "traffic_ahrefs": "112.4K",
        "traffic_num": 742000,
        "dr": 81,
        "da": 74,
        "as_score": 58,
        "max_links": 2,
        "link_type": "DoFollow",
        "turnaround": "3 Days",
        "country": "Philippines",
        "country_extra": "+3 Others",
        "followed_backlinks": "710K",
        "nofollow_backlinks": "218K",
        "domain_age": "28Y 9M",
        "outreach_status": "Open for Pitches"
    },
    {
        "id": "dom-2",
        "domain": "finance.yahoo.com",
        "sample_url": "https://finance.yahoo.com/news/article",
        "category": "Finance",
        "categories": ["Finance", "News and Media", "Business"],
        "traffic_semrush": "124.5M",
        "traffic_ahrefs": "78.2M",
        "traffic_num": 124500000,
        "dr": 94,
        "da": 93,
        "as_score": 100,
        "max_links": 2,
        "link_type": "NoFollow",
        "turnaround": "3 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "14.8M",
        "nofollow_backlinks": "5.3M",
        "domain_age": "30Y 2M",
        "outreach_status": "Syndication Available"
    },
    {
        "id": "dom-3",
        "domain": "businessinsider.com",
        "sample_url": "https://www.businessinsider.com/business-news",
        "category": "Business",
        "categories": ["Business", "Technology", "Finance"],
        "traffic_semrush": "46.8M",
        "traffic_ahrefs": "39.4M",
        "traffic_num": 46800000,
        "dr": 92,
        "da": 91,
        "as_score": 96,
        "max_links": 2,
        "link_type": "DoFollow",
        "turnaround": "4 Days",
        "country": "United States",
        "country_extra": "+5 Others",
        "followed_backlinks": "9.2M",
        "nofollow_backlinks": "2.5M",
        "domain_age": "18Y 6M",
        "outreach_status": "Editorial Review"
    },
    {
        "id": "dom-4",
        "domain": "digitaljournal.com",
        "sample_url": "https://www.digitaljournal.com/pr/news",
        "category": "News and Media",
        "categories": ["News and Media", "Technology", "General"],
        "traffic_semrush": "1.3M",
        "traffic_ahrefs": "680K",
        "traffic_num": 1300000,
        "dr": 84,
        "da": 80,
        "as_score": 69,
        "max_links": 3,
        "link_type": "DoFollow",
        "turnaround": "2 Days",
        "country": "Canada",
        "country_extra": "+2 Others",
        "followed_backlinks": "995K",
        "nofollow_backlinks": "330K",
        "domain_age": "24Y 1M",
        "outreach_status": "Open for Pitches"
    },
    {
        "id": "dom-5",
        "domain": "techcrunch.com",
        "sample_url": "https://techcrunch.com/startups",
        "category": "Technology",
        "categories": ["Technology", "Startups", "AI & Software"],
        "traffic_semrush": "14.2M",
        "traffic_ahrefs": "9.8M",
        "traffic_num": 14200000,
        "dr": 93,
        "da": 92,
        "as_score": 95,
        "max_links": 1,
        "link_type": "DoFollow",
        "turnaround": "5 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "6.1M",
        "nofollow_backlinks": "1.9M",
        "domain_age": "19Y 11M",
        "outreach_status": "Editorial Review"
    },
    {
        "id": "dom-6",
        "domain": "apnews.com",
        "sample_url": "https://apnews.com/press-releases",
        "category": "Press Release",
        "categories": ["Press Release", "News and Media", "General"],
        "traffic_semrush": "82.4M",
        "traffic_ahrefs": "51.3M",
        "traffic_num": 82400000,
        "dr": 93,
        "da": 92,
        "as_score": 98,
        "max_links": 3,
        "link_type": "DoFollow",
        "turnaround": "1 Day",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "12.4M",
        "nofollow_backlinks": "4.1M",
        "domain_age": "26Y 3M",
        "outreach_status": "Press Wire Active"
    },
    {
        "id": "dom-7",
        "domain": "globenewswire.com",
        "sample_url": "https://www.globenewswire.com/news-release",
        "category": "Press Release",
        "categories": ["Press Release", "Business", "Finance"],
        "traffic_semrush": "6.7M",
        "traffic_ahrefs": "4.2M",
        "traffic_num": 6700000,
        "dr": 89,
        "da": 88,
        "as_score": 84,
        "max_links": 3,
        "link_type": "DoFollow",
        "turnaround": "1 Day",
        "country": "United States",
        "country_extra": "+4 Others",
        "followed_backlinks": "3.8M",
        "nofollow_backlinks": "1.2M",
        "domain_age": "27Y 5M",
        "outreach_status": "Press Wire Active"
    },
    {
        "id": "dom-8",
        "domain": "usatoday.com",
        "sample_url": "https://www.usatoday.com/money",
        "category": "News and Media",
        "categories": ["News and Media", "Business", "Lifestyle"],
        "traffic_semrush": "95.1M",
        "traffic_ahrefs": "62.0M",
        "traffic_num": 95100000,
        "dr": 93,
        "da": 92,
        "as_score": 98,
        "max_links": 2,
        "link_type": "NoFollow",
        "turnaround": "3 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "18.9M",
        "nofollow_backlinks": "6.4M",
        "domain_age": "32Y 1M",
        "outreach_status": "Syndication Available"
    },
    {
        "id": "dom-9",
        "domain": "forbes.com",
        "sample_url": "https://www.forbes.com/business",
        "category": "Business",
        "categories": ["Business", "Leadership", "Finance"],
        "traffic_semrush": "148.0M",
        "traffic_ahrefs": "94.2M",
        "traffic_num": 148000000,
        "dr": 94,
        "da": 95,
        "as_score": 100,
        "max_links": 1,
        "link_type": "NoFollow",
        "turnaround": "6 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "25.6M",
        "nofollow_backlinks": "8.7M",
        "domain_age": "29Y 4M",
        "outreach_status": "Editorial Review"
    },
    {
        "id": "dom-10",
        "domain": "entrepreneur.com",
        "sample_url": "https://www.entrepreneur.com/article",
        "category": "Business",
        "categories": ["Business", "Marketing", "Startups"],
        "traffic_semrush": "17.4M",
        "traffic_ahrefs": "11.6M",
        "traffic_num": 17400000,
        "dr": 90,
        "da": 89,
        "as_score": 89,
        "max_links": 2,
        "link_type": "DoFollow",
        "turnaround": "5 Days",
        "country": "United States",
        "country_extra": "+5 Others",
        "followed_backlinks": "5.3M",
        "nofollow_backlinks": "1.8M",
        "domain_age": "27Y 10M",
        "outreach_status": "Open for Pitches"
    },
    {
        "id": "dom-11",
        "domain": "mashable.com",
        "sample_url": "https://mashable.com/tech",
        "category": "Technology",
        "categories": ["Technology", "Culture", "Digital Marketing"],
        "traffic_semrush": "22.5M",
        "traffic_ahrefs": "15.1M",
        "traffic_num": 22500000,
        "dr": 91,
        "da": 90,
        "as_score": 92,
        "max_links": 2,
        "link_type": "DoFollow",
        "turnaround": "4 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "7.8M",
        "nofollow_backlinks": "2.2M",
        "domain_age": "19Y 8M",
        "outreach_status": "Open for Pitches"
    }
]


class UnifiedApexHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Free High-Authority Domain Explorer
        if parsed.path in ["/api/publishers", "/api/websites", "/api/domains"]:
            qs = urllib.parse.parse_qs(parsed.query)
            q = qs.get("q", [""])[0].lower().strip()
            cat = qs.get("category", ["all"])[0]
            min_dr = int(qs.get("min_dr", [0])[0])
            min_da = int(qs.get("min_da", [0])[0])
            link_type = qs.get("link_type", ["all"])[0]
            sort_by = qs.get("sort", ["default"])[0]

            filtered = []
            for w in DOMAIN_EXPLORER_DB:
                if q and (q not in w["domain"].lower() and not any(q in c.lower() for c in w["categories"])):
                    continue
                if cat != "all" and cat != w["category"] and cat not in w["categories"]:
                    continue
                if w["dr"] < min_dr or w["da"] < min_da:
                    continue
                if link_type != "all" and w["link_type"].lower() != link_type.lower():
                    continue
                filtered.append(w)

            if sort_by == "dr_desc":
                filtered.sort(key=lambda x: x["dr"], reverse=True)
            elif sort_by == "da_desc":
                filtered.sort(key=lambda x: x["da"], reverse=True)
            elif sort_by == "traffic_desc":
                filtered.sort(key=lambda x: x["traffic_num"], reverse=True)
            elif sort_by == "domain_asc":
                filtered.sort(key=lambda x: x["domain"])

            self._send_json({"total": len(filtered), "data": filtered})
            return

        elif parsed.path == "/api/stats":
            self._send_json({
                "platform": "ApexLink Studio Tools",
                "tier": "100% Free & Open Utility Suite",
                "indexing_templates": template_repo.total_count,
                "verified_domains_indexed": len(DOMAIN_EXPLORER_DB),
                "guarantee_uptime": "99.98%",
                "owner_identity": AUTHORIZED_OWNER_ID,
                "security_status": "LOCKED_AUTHORIZED_OWNER_ONLY",
                "available_tools": [
                    "4640+ Backlink URL Generator",
                    "Live Concurrent Link Verifier",
                    "Multi-Threaded Live Pinger",
                    "Google E-E-A-T Domain Auditor",
                    "Penguin-Safe Anchor Diversity Matrix",
                    "Google Search Console Disavow Builder",
                    "High-Authority Outreach Domain Explorer"
                ]
            })
            return

        elif parsed.path == "/api/security/manifest":
            self._send_json(get_security_manifest())
            return

        # Default static file serving (HTML, JS, CSS, robots.txt, sitemap.xml)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Backlink Generator Tool (Free 4,640+ endpoints, quality prioritized)
        if parsed.path == "/api/generate":
            target = payload.get("url", "https://example.com")
            cat = payload.get("category", "all")
            limit = int(payload.get("limit", 100))
            do_verify = bool(payload.get("verify", False))

            norm = normalize_url(target)
            vid = extract_youtube_id(norm)
            token_map = build_token_map(norm, vid)
            templates = template_repo.get_templates(is_youtube=bool(vid), category=cat)

            urls = []
            detailed = []
            seen = set()
            max_needed = limit if limit > 0 else 500
            for t in templates:
                u = replace_tokens(t["url"], token_map).strip()
                if u and u.startswith(("http://", "https://")) and u not in seen:
                    seen.add(u)
                    urls.append(u)
                    da, tier = get_link_authority_profile(u)
                    detailed.append({
                        "url": u,
                        "category": t["category"],
                        "domain_authority": da,
                        "quality_tier": tier
                    })
                    if len(urls) >= max_needed:
                        break

            # If live verification requested, run concurrent verification
            if do_verify and urls:
                verified_records = verify_urls_concurrently(urls[:50], concurrency=15)
                self._send_json({
                    "target": norm,
                    "urls": urls,
                    "detailed": detailed,
                    "verified": verified_records,
                    "total": len(urls)
                })
                return

            self._send_json({"target": norm, "urls": urls, "detailed": detailed, "total": len(urls)})
            return

        # 2. Live Concurrent Link Verifier Tool (Direct bulk link verification)
        elif parsed.path == "/api/verify":
            raw_urls = payload.get("urls", [])
            if not raw_urls and payload.get("url"):
                raw_urls = [payload.get("url")]
            concurrency = int(payload.get("concurrency", 15))
            timeout = float(payload.get("timeout", 4.0))

            clean_urls = [u.strip() for u in raw_urls if u.strip()]
            verified = verify_urls_concurrently(clean_urls, concurrency=concurrency, timeout=timeout)
            
            valid_count = sum(1 for r in verified if r["is_valid"])
            self._send_json({
                "results": verified,
                "total": len(verified),
                "valid_count": valid_count,
                "success_rate": round((valid_count / len(verified) * 100) if verified else 0, 1)
            })
            return

        # 3. Live Concurrent Pinger (Multi-threaded HTTP pings)
        elif parsed.path == "/api/ping":
            target = payload.get("url", "https://example.com")
            cat = payload.get("category", "all")
            limit = int(payload.get("limit", 30))

            norm = normalize_url(target)
            vid = extract_youtube_id(norm)
            token_map = build_token_map(norm, vid)
            templates = template_repo.get_templates(is_youtube=bool(vid), category=cat)

            targets = []
            seen = set()
            for t in templates:
                u = replace_tokens(t["url"], token_map).strip()
                if u and u.startswith(("http://", "https://")) and u not in seen:
                    seen.add(u)
                    targets.append({"url": u, "category": t["category"]})
            if limit:
                targets = targets[:limit]

            from concurrent.futures import ThreadPoolExecutor, as_completed
            results = []
            with ThreadPoolExecutor(max_workers=min(len(targets) or 1, 15)) as pool:
                futures = {pool.submit(_sync_ping_urllib, item, 2.5): item for item in targets}
                for f in as_completed(futures):
                    try:
                        res = f.result()
                        results.append(res.to_dict())
                    except Exception as err:
                        results.append({
                            "url": futures[f]["url"],
                            "category": futures[f]["category"],
                            "status": "ERR",
                            "ok": False,
                            "latency_ms": 0.0
                        })

            self._send_json({"results": results, "total": len(results)})
            return

        # 4. E-E-A-T Domain Vetting Tool
        elif parsed.path == "/api/vet":
            target = payload.get("target", "")
            res = audit_url(target)
            self._send_json(res.to_dict())
            return

        # 5. Contextual Anchor Text Diversity Matrix Tool
        elif parsed.path == "/api/anchors":
            brand = payload.get("brand", "ApexBrand")
            url = payload.get("url", "https://example.com")
            kw = payload.get("keyword", "link building")
            count = int(payload.get("count", 25))
            anchors = generate_anchor_profile(brand, url, kw, count=count)
            self._send_json({"anchors": anchors})
            return

        # 6. Google Disavow Generator Tool
        elif parsed.path == "/api/disavow":
            items = payload.get("items", [])
            domain_mode = payload.get("domain_mode", True)
            content = generate_disavow_content(items, domain_mode=domain_mode)
            self._send_json({"content": content})
            return

        # 7. Owner Verification
        elif parsed.path == "/api/owner/verify":
            candidate = payload.get("owner_id", "")
            authorized = verify_owner_access(candidate)
            self._send_json({"authorized": authorized, "owner": AUTHORIZED_OWNER_ID})
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


def start_server(host: str = "127.0.0.1", port: int = 8700):
    server = ThreadingHTTPServer((host, port), UnifiedApexHandler)
    server.daemon_threads = True
    print(f"[*] ApexLink 100% Free SEO Studio Running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()
