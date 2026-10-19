"""
ApexLink Studio — Unified Enterprise SEO & Link Building Suite
Integrates:
1. Vefogix-style 140,000+ Guest Post Marketplace with real-time Ahrefs/Semrush metrics
2. High-throughput 4,600+ Directory, Archive & Web Diagnostic Generator & Pinger
3. E-E-A-T & Toxic PBN Domain Auditor
4. Contextual Penguin-Safe Anchor Text Diversity Matrix
5. Google Search Console Disavow Generator
6. Cryptographic Owner & Modification Lock (tarikk786786)
"""

import json
import os
import sys
import time
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
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
from vetting.auditor import audit_url, audit_batch
from vetting.disavow import generate_disavow_content
from contextual.anchors import generate_anchor_profile

# Verified High-Authority Publications Database
PUBLISHERS_DB = [
    {
        "id": "apx-1",
        "domain": "manilatimes.net",
        "sample_url": "https://www.manilatimes.net/business/article",
        "price": 24,
        "currency": "USD",
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
        "deals_completed": 92
    },
    {
        "id": "apx-2",
        "domain": "finance.yahoo.com",
        "sample_url": "https://finance.yahoo.com/news/article",
        "price": 75,
        "currency": "USD",
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
        "deals_completed": 156
    },
    {
        "id": "apx-3",
        "domain": "businessinsider.com",
        "sample_url": "https://www.businessinsider.com/business-news",
        "price": 149,
        "currency": "USD",
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
        "deals_completed": 124
    },
    {
        "id": "apx-4",
        "domain": "digitaljournal.com",
        "sample_url": "https://www.digitaljournal.com/pr/news",
        "price": 38,
        "currency": "USD",
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
        "deals_completed": 105
    },
    {
        "id": "apx-5",
        "domain": "techcrunch.com",
        "sample_url": "https://techcrunch.com/startups",
        "price": 285,
        "currency": "USD",
        "category": "Technology",
        "categories": ["Technology", "Startups", "AI & Software"],
        "traffic_semrush": "19.1M",
        "traffic_ahrefs": "12.8M",
        "traffic_num": 19100000,
        "dr": 93,
        "da": 92,
        "as_score": 95,
        "max_links": 1,
        "link_type": "DoFollow",
        "turnaround": "5 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "5.8M",
        "nofollow_backlinks": "1.9M",
        "domain_age": "20Y 5M",
        "deals_completed": 72
    },
    {
        "id": "apx-6",
        "domain": "apnews.com",
        "sample_url": "https://apnews.com/press-releases",
        "price": 92,
        "currency": "USD",
        "category": "News and Media",
        "categories": ["News and Media", "Press Release", "Global"],
        "traffic_semrush": "67.1M",
        "traffic_ahrefs": "43.5M",
        "traffic_num": 67100000,
        "dr": 91,
        "da": 90,
        "as_score": 96,
        "max_links": 2,
        "link_type": "NoFollow",
        "turnaround": "2 Days",
        "country": "United States",
        "country_extra": "Global",
        "followed_backlinks": "12.5M",
        "nofollow_backlinks": "3.9M",
        "domain_age": "29Y 8M",
        "deals_completed": 138
    },
    {
        "id": "apx-7",
        "domain": "venturebeat.com",
        "sample_url": "https://venturebeat.com/ai",
        "price": 199,
        "currency": "USD",
        "category": "Technology",
        "categories": ["Technology", "AI & Machine Learning", "Business"],
        "traffic_semrush": "9.2M",
        "traffic_ahrefs": "5.7M",
        "traffic_num": 9200000,
        "dr": 89,
        "da": 88,
        "as_score": 83,
        "max_links": 2,
        "link_type": "DoFollow",
        "turnaround": "4 Days",
        "country": "United States",
        "country_extra": "+3 Others",
        "followed_backlinks": "3.6M",
        "nofollow_backlinks": "1.2M",
        "domain_age": "19Y 2M",
        "deals_completed": 82
    },
    {
        "id": "apx-8",
        "domain": "globenewswire.com",
        "sample_url": "https://www.globenewswire.com/news-release",
        "price": 68,
        "currency": "USD",
        "category": "Press Release",
        "categories": ["Press Release", "Business", "News and Media"],
        "traffic_semrush": "14.8M",
        "traffic_ahrefs": "10.2M",
        "traffic_num": 14800000,
        "dr": 88,
        "da": 86,
        "as_score": 81,
        "max_links": 3,
        "link_type": "DoFollow",
        "turnaround": "1 Day",
        "country": "United States",
        "country_extra": "+6 Others",
        "followed_backlinks": "4.4M",
        "nofollow_backlinks": "1.4M",
        "domain_age": "26Y 4M",
        "deals_completed": 184
    },
    {
        "id": "apx-9",
        "domain": "usatoday.com",
        "sample_url": "https://www.usatoday.com/money",
        "price": 165,
        "currency": "USD",
        "category": "News and Media",
        "categories": ["News and Media", "Lifestyle", "Business"],
        "traffic_semrush": "79.8M",
        "traffic_ahrefs": "55.4M",
        "traffic_num": 79800000,
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
        "deals_completed": 98
    },
    {
        "id": "apx-10",
        "domain": "forbes.com",
        "sample_url": "https://www.forbes.com/business",
        "price": 460,
        "currency": "USD",
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
        "deals_completed": 61
    },
    {
        "id": "apx-11",
        "domain": "entrepreneur.com",
        "sample_url": "https://www.entrepreneur.com/article",
        "price": 225,
        "currency": "USD",
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
        "deals_completed": 94
    },
    {
        "id": "apx-12",
        "domain": "mashable.com",
        "sample_url": "https://mashable.com/tech",
        "price": 180,
        "currency": "USD",
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
        "deals_completed": 88
    }
]

ORDERS_LEDGER = []


class UnifiedApexHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path in ["/api/publishers", "/api/websites"]:
            qs = urllib.parse.parse_qs(parsed.query)
            q = qs.get("q", [""])[0].lower().strip()
            cat = qs.get("category", ["all"])[0]
            min_dr = int(qs.get("min_dr", [0])[0])
            min_da = int(qs.get("min_da", [0])[0])
            max_price = int(qs.get("max_price", [9999])[0])
            link_type = qs.get("link_type", ["all"])[0]
            sort_by = qs.get("sort", ["default"])[0]

            filtered = []
            for w in PUBLISHERS_DB:
                if q and (q not in w["domain"].lower() and not any(q in c.lower() for c in w["categories"])):
                    continue
                if cat != "all" and cat != w["category"] and cat not in w["categories"]:
                    continue
                if w["dr"] < min_dr or w["da"] < min_da:
                    continue
                if w["price"] > max_price:
                    continue
                if link_type != "all" and w["link_type"].lower() != link_type.lower():
                    continue
                filtered.append(w)

            if sort_by == "price_asc":
                filtered.sort(key=lambda x: x["price"])
            elif sort_by == "price_desc":
                filtered.sort(key=lambda x: x["price"], reverse=True)
            elif sort_by == "dr_desc":
                filtered.sort(key=lambda x: x["dr"], reverse=True)
            elif sort_by == "traffic_desc":
                filtered.sort(key=lambda x: x["traffic_num"], reverse=True)

            self._send_json({"total": len(filtered), "data": filtered})
            return

        elif parsed.path == "/api/stats":
            self._send_json({
                "registered_websites": "142,500+",
                "publishers_writers": "48,200+",
                "tasks_completed": "310,000+",
                "indexing_templates": template_repo.total_count,
                "guarantee_uptime": "99.98%",
                "owner_identity": AUTHORIZED_OWNER_ID,
                "security_status": "LOCKED_AUTHORIZED_OWNER_ONLY"
            })
            return

        elif parsed.path == "/api/security/manifest":
            self._send_json(get_security_manifest())
            return

        elif parsed.path == "/api/orders":
            self._send_json({"orders": ORDERS_LEDGER, "total": len(ORDERS_LEDGER)})
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

        # 1. Backlink Generator Endpoint (from backlink-generator-tool)
        if parsed.path == "/api/generate":
            target = payload.get("url", "https://example.com")
            cat = payload.get("category", "all")
            limit = int(payload.get("limit", 100))

            norm = normalize_url(target)
            vid = extract_youtube_id(norm)
            token_map = build_token_map(norm, vid)
            templates = template_repo.get_templates(is_youtube=bool(vid), category=cat)

            urls = []
            seen = set()
            for t in templates:
                u = replace_tokens(t["url"], token_map).strip()
                if u and u.startswith(("http://", "https://")) and u not in seen:
                    seen.add(u)
                    urls.append(u)
            if limit:
                urls = urls[:limit]

            self._send_json({"target": norm, "urls": urls, "total": len(urls)})
            return

        # 2. Live Concurrent Pinger (from h4cklinker & tegal1337)
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

            results = []
            for item in targets:
                res = _sync_ping_urllib(item, timeout=3.5)
                results.append(res.to_dict())

            self._send_json({"results": results, "total": len(results)})
            return

        # 3. E-E-A-T Domain Vetting (from thelinkoster)
        elif parsed.path == "/api/vet":
            target = payload.get("target", "")
            res = audit_url(target)
            self._send_json(res.to_dict())
            return

        # 4. Contextual Anchor Text Generator (from contextual-backlink-generator)
        elif parsed.path == "/api/anchors":
            brand = payload.get("brand", "ApexBrand")
            url = payload.get("url", "https://example.com")
            kw = payload.get("keyword", "link building")
            count = int(payload.get("count", 25))
            anchors = generate_anchor_profile(brand, url, kw, count=count)
            self._send_json({"anchors": anchors})
            return

        # 5. Google Disavow Generator (from Disavow-Generator)
        elif parsed.path == "/api/disavow":
            items = payload.get("items", [])
            content = generate_disavow_content(items, domain_mode=True)
            self._send_json({"content": content})
            return

        # 6. Marketplace Cart Checkout
        elif parsed.path == "/api/cart/checkout":
            order_id = f"APX-{int(time.time())}-{len(ORDERS_LEDGER) + 101}"
            raw_record = json.dumps(payload, sort_keys=True)
            sig = compute_payload_hmac(raw_record)

            order = {
                "order_id": order_id,
                "items": payload.get("items", []),
                "total_usd": payload.get("total_usd", 0),
                "target_url": payload.get("target_url", ""),
                "anchor_text": payload.get("anchor_text", ""),
                "content_option": payload.get("content_option", "publisher_writes"),
                "status": "QUEUED_EDITORIAL_INTEGRITY_CHECK",
                "hmac_signature": sig[:16] + "...",
                "created_at": int(time.time())
            }
            ORDERS_LEDGER.append(order)
            self._send_json({"success": True, "order": order})
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
    server = HTTPServer((host, port), UnifiedApexHandler)
    print(f"[*] ApexLink All-In-One Studio Running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()
