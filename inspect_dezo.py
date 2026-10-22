import urllib.request
import ssl
import re
import json

ctx = ssl._create_unverified_context()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

req = urllib.request.Request('https://dezo.in/', headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')
        print(f"HTTP Status: {r.getcode()}")
        print(f"HTML Size: {len(html)} bytes")
        
        m_title = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
        title = m_title.group(1).strip() if m_title else "No Title"
        print(f"Title: {title}")
        
        m_desc = re.search(r'<meta[^>]*name=[\'"]description[\'"][^>]*content=[\'"](.*?)[\'"]', html, re.I)
        desc = m_desc.group(1).strip() if m_desc else "No Description"
        print(f"Meta Description: {desc}")
        
        h1s = [re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.S)]
        print(f"H1 Tags: {h1s}")

        h2s = [re.sub(r'<[^>]+>', '', h).strip() for h in re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.I | re.S)]
        print(f"H2 Tags (top 5): {h2s[:5]}")
        
        links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html, re.I)
        internal = [l for l in links if l.startswith('/') or 'dezo.in' in l]
        external = [l for l in links if l.startswith('http') and 'dezo.in' not in l]
        print(f"Internal Links Count: {len(internal)}, External Links Count: {len(external)}")
        print(f"Sample Internal: {internal[:5]}")
        
except Exception as ex:
    print(f"Fetch Error: {ex}")
