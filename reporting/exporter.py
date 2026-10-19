"""
Multi-Format Export & Audit Reporting Engine
Exports backlink results, audit logs, and metrics to CSV, JSON, TXT, and Markdown reports.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def export_urls_txt(urls: List[str], output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")
    return str(path.resolve())


def export_results_csv(results: List[Dict], output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if not results:
        with open(path, "w", encoding="utf-8") as f:
            f.write("url,category,status,ok,latency_ms\n")
        return str(path.resolve())

    fieldnames = ["url", "category", "status", "ok", "latency_ms"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    return str(path.resolve())


def export_results_json(data: Dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(path.resolve())


def generate_markdown_report(target_url: str, total_generated: int, ping_results: List[Dict] = None, output_path: str = "report.md") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    successes = sum(1 for r in ping_results if r.get("ok")) if ping_results else 0
    total_pinged = len(ping_results) if ping_results else 0
    rate = f"{(successes / total_pinged * 100):.1f}%" if total_pinged > 0 else "N/A"

    lines = [
        f"# OmniLink Studio - SEO Backlink & Indexing Report",
        f"**Target URL:** `{target_url}`  ",
        f"**Generated:** {timestamp}  ",
        f"",
        f"## 📊 Execution Summary",
        f"- **Total Endpoints Generated:** {total_generated}",
        f"- **Endpoints Pinged:** {total_pinged}",
        f"- **Successful Indexing Signals (2xx/3xx):** {successes}",
        f"- **Success Rate:** {rate}",
        f"",
        f"## 🌐 Category Distribution",
    ]

    if ping_results:
        cat_counts: Dict[str, int] = {}
        for r in ping_results:
            c = r.get("category", "other")
            cat_counts[c] = cat_counts.get(c, 0) + 1

        lines.append("| Category | Endpoints Pinged |")
        lines.append("| :--- | :--- |")
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| `{cat}` | {cnt} |")
        lines.append("")

        lines.append("## 🔍 Sample Results (First 15)")
        lines.append("| Status | Category | Endpoint URL | Latency |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for r in ping_results[:15]:
            status_badge = "✅ " + str(r.get("status")) if r.get("ok") else "⚠️ " + str(r.get("status"))
            lines.append(f"| {status_badge} | `{r.get('category')}` | {r.get('url')[:60]}... | {r.get('latency_ms', 0)}ms |")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return str(path.resolve())
