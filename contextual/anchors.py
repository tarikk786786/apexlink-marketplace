"""
Contextual Anchor Text Diversity Matrix
Generates mathematically balanced anchor text distributions to prevent Google Penguin over-optimization penalties.
Synthesizes techniques from contextual-backlink-generator.
"""

import random
from typing import Dict, List


GENERIC_ANCHORS = [
    "click here", "visit website", "read more", "learn more",
    "official website", "source", "view source", "link",
    "check this out", "more information", "reference"
]


def generate_anchor_profile(
    brand_name: str,
    target_url: str,
    primary_keyword: str,
    secondary_keywords: List[str] = None,
    count: int = 100
) -> List[Dict[str, str]]:
    """
    Constructs a natural anchor text distribution:
    - 45% Branded
    - 25% Naked URL
    - 15% Partial Match / Compound
    - 10% Generic Call to Action
    - 5% Exact Match
    """
    if not secondary_keywords:
        secondary_keywords = ["best tools", "guide", "platform", "online software", "solutions"]

    clean_domain = target_url.replace("https://", "").replace("http://", "").rstrip("/")
    naked_variants = [
        target_url,
        clean_domain,
        f"www.{clean_domain}" if not clean_domain.startswith("www.") else clean_domain,
        clean_domain.lower()
    ]

    branded_variants = [
        brand_name,
        brand_name.lower(),
        brand_name.upper(),
        f"{brand_name} Official",
        f"{brand_name} Platform",
        f"{brand_name} Tools"
    ]

    partial_variants = []
    for sk in secondary_keywords:
        partial_variants.append(f"{brand_name} {sk}")
        partial_variants.append(f"{primary_keyword} by {brand_name}")
        partial_variants.append(f"{sk} on {brand_name}")

    exact_variants = [primary_keyword, primary_keyword.lower()]

    profile: List[Dict[str, str]] = []

    for _ in range(count):
        roll = random.random()
        if roll < 0.45:
            anchor = random.choice(branded_variants)
            tier = "BRANDED"
        elif roll < 0.70:
            anchor = random.choice(naked_variants)
            tier = "NAKED_URL"
        elif roll < 0.85:
            anchor = random.choice(partial_variants)
            tier = "PARTIAL_MATCH"
        elif roll < 0.95:
            anchor = random.choice(GENERIC_ANCHORS)
            tier = "GENERIC_CTA"
        else:
            anchor = random.choice(exact_variants)
            tier = "EXACT_MATCH"

        profile.append({"anchor": anchor, "tier": tier, "target_url": target_url})

    return profile
