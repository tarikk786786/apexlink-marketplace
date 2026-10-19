"""
Universal URL Tokenizer & Substitution Engine
Handles URL parsing, normalization, YouTube detection, and placeholder token mapping.
Compatible with templates from backlink-generator-tool, h4cklinker, and tegal1337.
"""

import re
import urllib.parse
from typing import Dict, Optional


def normalize_url(raw_url: str) -> str:
    """Ensure standard URL formatting with scheme and trimmed whitespace."""
    url = raw_url.strip()
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    return url


def extract_youtube_id(url_str: str) -> Optional[str]:
    """Extract YouTube Video ID if present in URL."""
    try:
        parsed = urllib.parse.urlparse(url_str)
        host = (parsed.hostname or "").lower()
        if "youtube.com" in host:
            qs = urllib.parse.parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
        elif "youtu.be" in host:
            clean_path = parsed.path.strip("/")
            if clean_path:
                return clean_path.split("/")[0]
    except Exception:
        pass
    return None


def build_token_map(target_url: str, video_id: Optional[str] = None) -> Dict[str, str]:
    """
    Constructs comprehensive token mapping for template substitutions.
    Produces both standard and URL-encoded variants (e.g. [DOMAIN], [ENCODE_DOMAIN]).
    """
    p = urllib.parse.urlparse(target_url)
    hostname = p.hostname or ""
    parts = hostname.split(".")
    ln = len(parts)

    hostname_no_www = re.sub(r"^www\.", "", hostname, flags=re.IGNORECASE)
    
    subdomain = ".".join(parts[:-2]) + "." if ln > 2 else ""
    domain_name = parts[-2] if ln >= 2 else (parts[0] if parts else "")
    tld = parts[-1] if ln >= 2 else ""
    port = f":{p.port}" if p.port else ""
    path = p.path or "/"
    query = f"?{p.query}" if p.query else ""
    params = p.query or ""
    fragment = f"#{p.fragment}" if p.fragment else ""
    
    no_protocol_url = f"{hostname}{port}{path}{query}{fragment}"
    no_subdomain_url = f"{hostname_no_www}{port}{path}{query}{fragment}"

    data: Dict[str, str] = {
        "PROTOCOL": p.scheme + ":" if p.scheme else "https:",
        "SUBDOMAIN": subdomain,
        "DOMAINNAME": domain_name,
        "TLD": tld,
        "HOST": f"{hostname}{port}",
        "PORT": port,
        "PATH": path,
        "QUERY": query,
        "PARAMS": params,
        "FRAGMENT": fragment,
        "URL": target_url,
        "DOMAIN": hostname,
        "NOPROTOCOL_URL": no_protocol_url,
        "NOSUBDOMAIN_URL": no_subdomain_url,
    }
    
    if video_id:
        data["ID"] = video_id

    # Generate uppercase and URL-encoded variants
    encoded: Dict[str, str] = {}
    for k, v in data.items():
        encoded[f"ENCODE_{k}"] = urllib.parse.quote(str(v), safe="")
    data.update(encoded)
    return data


def replace_tokens(template: str, token_map: Dict[str, str]) -> str:
    """
    Substitutes token placeholders in various syntax formats:
    - [TOKEN] / [ENCODE_TOKEN]
    - {{TOKEN}} / {{ENCODE_TOKEN}}
    - %5BTOKEN%5D / %7B%7BTOKEN%7D%7D
    """
    if not template:
        return ""

    # Normalize encoded brackets
    t = template
    t = re.sub(r"%5B\s*(ENCODE_)?([A-Z0-9_]+)\s*%5D", r"[\1\2]", t, flags=re.I)
    t = re.sub(r"&#(?:x5b|91);\s*(ENCODE_)?([A-Z0-9_]+)\s*&#(?:x5d|93);", r"[\1\2]", t, flags=re.I)
    t = re.sub(r"\{\{\s*(ENCODE_)?([A-Z0-9_]+)\s*\}\}", r"[\1\2]", t, flags=re.I)
    t = re.sub(r"%7B%7B\s*(ENCODE_)?([A-Z0-9_]+)\s*%7D%7D", r"[\1\2]", t, flags=re.I)

    def repl(m: re.Match) -> str:
        enc_prefix = m.group(2)
        key = (m.group(3) or "").upper()
        offset = m.start()
        
        wants_encode = bool(enc_prefix)
        if wants_encode:
            encoded_key = f"ENCODE_{key}"
            if encoded_key in token_map:
                return token_map[encoded_key]
            return urllib.parse.quote(str(token_map.get(key, "")), safe="")
        
        # If the parameter is preceded by "url=", ensure it gets safely encoded
        if key == "URL":
            before = t[max(0, offset - 30):offset].lower()
            if re.search(r"\burl\s*=\s*$", before) or re.search(r"\burl\s*=", t, re.I):
                return urllib.parse.quote(str(token_map.get("URL", "")), safe="")

        return str(token_map.get(key, ""))

    return re.sub(r"(\{\{|\[)\s*(ENCODE_)?([A-Z0-9_]+)\s*(\}\}|\])", repl, t, flags=re.I)
