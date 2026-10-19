"""
High-Throughput Asynchronous Pinger Engine
Submits URL indexing signals across hundreds of endpoints concurrently.
Supports aiohttp with graceful fallback to ThreadPoolExecutor for 100% zero-dependency execution.
"""

import asyncio
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    import urllib.request

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 OmniLink/1.0"
)


class PingResult:
    def __init__(self, url: str, category: str, status: str, ok: bool, latency_ms: float = 0.0):
        self.url = url
        self.category = category
        self.status = status
        self.ok = ok
        self.latency_ms = latency_ms

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "category": self.category,
            "status": self.status,
            "ok": self.ok,
            "latency_ms": round(self.latency_ms, 2)
        }


async def _ping_aiohttp(session: "aiohttp.ClientSession", item: Dict[str, str], sem: asyncio.Semaphore, timeout: float) -> PingResult:
    url = item["url"]
    category = item.get("category", "directory")
    start = time.perf_counter()
    async with sem:
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                allow_redirects=True,
                ssl=False
            ) as resp:
                elapsed = (time.perf_counter() - start) * 1000
                is_ok = resp.status < 400
                return PingResult(url, category, str(resp.status), is_ok, elapsed)
        except asyncio.TimeoutError:
            elapsed = (time.perf_counter() - start) * 1000
            return PingResult(url, category, "TIMEOUT", False, elapsed)
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            err_name = type(e).__name__
            return PingResult(url, category, f"ERR_{err_name}", False, elapsed)


def _sync_ping_urllib(item: Dict[str, str], timeout: float, proxy: Optional[str] = None) -> PingResult:
    import urllib.request
    import urllib.error
    url = item["url"]
    category = item.get("category", "directory")
    start = time.perf_counter()
    
    headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": "*/*"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        if proxy:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(proxy_handler)
        else:
            opener = urllib.request.build_opener()
            
        with opener.open(req, timeout=timeout) as resp:
            elapsed = (time.perf_counter() - start) * 1000
            code = resp.getcode()
            return PingResult(url, category, str(code), code < 400, elapsed)
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - start) * 1000
        return PingResult(url, category, str(e.code), False, elapsed)
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return PingResult(url, category, f"ERR_{type(e).__name__}", False, elapsed)


class AsyncPinger:
    def __init__(self, concurrency: int = 15, timeout: float = 6.0, proxy: Optional[str] = None):
        self.concurrency = max(1, min(concurrency, 100))
        self.timeout = timeout
        self.proxy = proxy

    async def run(
        self,
        targets: List[Dict[str, str]],
        progress_cb: Optional[Callable[[int, int, PingResult], None]] = None
    ) -> List[PingResult]:
        total = len(targets)
        results: List[PingResult] = []

        if HAS_AIOHTTP:
            connector = aiohttp.TCPConnector(ssl=False, limit=self.concurrency * 2)
            headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": "*/*"}
            sem = asyncio.Semaphore(self.concurrency)
            
            async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
                tasks = [_ping_aiohttp(session, item, sem, self.timeout) for item in targets]
                completed = 0
                for task in asyncio.as_completed(tasks):
                    res = await task
                    results.append(res)
                    completed += 1
                    if progress_cb:
                        progress_cb(completed, total, res)
        else:
            # Multi-threaded Fallback for environments without aiohttp
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                completed = 0
                futures = [
                    loop.run_in_executor(executor, _sync_ping_urllib, item, self.timeout, self.proxy)
                    for item in targets
                ]
                for fut in asyncio.as_completed(futures):
                    res = await fut
                    results.append(res)
                    completed += 1
                    if progress_cb:
                        progress_cb(completed, total, res)

        return results
