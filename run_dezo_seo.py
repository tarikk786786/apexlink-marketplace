"""
Comprehensive SEO Engine Campaign for https://dezo.in/
Executes all 7 ApexLink Studio tools against https://dezo.in/ :
1. Google E-E-A-T & Technical Audit
2. High-DA Quality Backlink Generator (Tier 1 & Tier 2)
3. Live Concurrent Link Verifier (Checking generated high-authority links)
4. Multi-Threaded Live Pinger & Search Engine Crawler Broadcaster
5. Penguin-Safe Anchor Text Diversity Matrix (Brand, Exact, Partial, Generic)
6. Google Search Console Disavow & Toxicity Shield
7. Export comprehensive campaign report and artifact
"""

import json
import urllib.request
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8700"
TARGET_URL = "https://dezo.in"
TARGET_DOMAIN = "dezo.in"
BRAND_NAME = "DEZO"
PRIMARY_KEYWORD = "digital infrastructure agency"

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("==================================================")
print(f"[*] LAUNCHING COMPLETE SEO ENGINE FOR {TARGET_URL}")
print("==================================================")

# Step 1: E-E-A-T & Domain Audit
print("\n[1/6] Running Google E-E-A-T & Domain Safety Audit...")
audit_res = post_json("/api/vet", {"target": TARGET_URL})
print(f" -> Trust Score: {audit_res.get('trust_score')}/100")
print(f" -> Authority Score: {audit_res.get('authority_score')}/100")
print(f" -> Toxic PBN Risk: {audit_res.get('pbn_risk')}")
print(f" -> Recommended Strategy: {audit_res.get('recommendation')}")

# Step 2: Contextual Penguin-Safe Anchor Text Matrix
print("\n[2/6] Generating Penguin-Safe Anchor Text Diversity Matrix...")
anchor_res = post_json("/api/anchors", {
    "brand": BRAND_NAME,
    "keyword": PRIMARY_KEYWORD,
    "url": TARGET_URL
})
anchors = anchor_res.get("anchors", [])
by_tier = {}
for a in anchors:
    by_tier.setdefault(a["tier"], []).append(a["anchor"])

for tier, items in by_tier.items():
    print(f" -> {tier} ({len(items)} items): {items[:3]}")

# Step 3: High-Quality Backlink Generation (Tier 1 & Tier 2) + Live Verification
print("\n[3/6] Generating High-Authority Backlink URLs (Tier 1 DA 85-99, Tier 2 DA 60-84)...")
gen_res = post_json("/api/generate", {
    "url": TARGET_URL,
    "category": "all",
    "limit": 50,
    "verify": True
})
gen_urls = gen_res.get("urls", [])
verified = gen_res.get("verified", [])
detailed = gen_res.get("detailed", [])
print(f" -> Generated {len(gen_urls)} High-DA Endpoints for {TARGET_URL}")
print(f" -> Live Verified Active Endpoints: {len([v for v in verified if v.get('is_valid')])}/{len(verified)}")

# Step 4: Bulk Live Verification of Top Seeds
print("\n[4/6] Verifying Tier 1 Live Indexing Authority Seeds...")
test_seeds = [
    f"https://web.archive.org/web/*/{TARGET_URL}",
    f"https://validator.w3.org/nu/?doc={TARGET_URL}",
    f"https://builtwith.com/?{TARGET_DOMAIN}",
    f"https://www.similarweb.com/website/{TARGET_DOMAIN}/",
    f"https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{TARGET_DOMAIN}&run=toolpage",
    f"https://viewdns.info/whois/?domain={TARGET_DOMAIN}",
    f"https://www.google.com/search?q=site%3A{TARGET_DOMAIN}"
]
verifier_res = post_json("/api/verify", {"urls": test_seeds})
print(f" -> Tested {verifier_res.get('total')} authority platforms | Success Rate: {verifier_res.get('success_rate')}%")
for item in verifier_res.get("results", []):
    status_sym = "[OK 200]" if item.get("is_valid") else f"[{item.get('status_code')}]"
    print(f"    {status_sym} {item.get('url')[:65]}... (DA {item.get('authority_da')} - {item.get('latency_ms')}ms)")

# Step 5: Multi-Threaded Live Pinger & Search Engine Broadcaster
print("\n[5/6] Broadcasting Live Pings to Global Search Crawlers & Aggregators...")
ping_res = post_json("/api/ping", {
    "url": TARGET_URL,
    "limit": 20
})
ping_results = ping_res.get("results", [])
success_pings = [p for p in ping_results if p.get("ok")]
print(f" -> Dispatched {len(ping_results)} concurrent crawler pings | Received {len(success_pings)} immediate OK acknowledgments")

# Step 6: Google Search Console Disavow Protection File
print("\n[6/6] Generating Algorithmic Disavow File (Google Search Console)...")
disavow_res = post_json("/api/disavow", {
    "toxic_domains": [
        "free-traffic-bot.xyz",
        "cheap-pbn-blast.club",
        "rank-fast-auto.top",
        "spamlinkfarm.online"
    ]
})
disavow_content = disavow_res.get("content", "")
print(" -> Disavow snippet generated successfully.")

# Save Full Campaign Artifact
output_data = {
    "target": TARGET_URL,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "audit": audit_res,
    "anchors": anchors,
    "generated_count": len(gen_urls),
    "detailed_links": detailed[:25],
    "verified_sample": verified[:15],
    "authority_seeds": verifier_res.get("results", []),
    "ping_results": ping_results[:10],
    "disavow_content": disavow_content
}

with open("dezo_seo_campaign_results.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)

print("\n[SUCCESS] Entire SEO Execution Complete. Campaign results written to dezo_seo_campaign_results.json")
