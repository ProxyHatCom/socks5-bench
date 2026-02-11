from __future__ import annotations

import asyncio
import time
from typing import Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector

from socks5_bench.models import BenchmarkResult, Proxy, ProbeResult, RotationResult

DEFAULT_TARGET = "https://httpbin.org/ip"
GEO_TARGET = "http://ip-api.com/json"


def _extract_ip(body: dict) -> Optional[str]:
    for key in ("origin", "ip", "query"):
        if key in body:
            return body[key]
    return None


def _extract_country(body: dict) -> Optional[str]:
    for key in ("country", "countryCode"):
        if key in body:
            return body[key]
    return None


def _percentile(sorted_data: list[float], p: float) -> float:
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


async def probe_once(proxy: Proxy, target: str, timeout_sec: float) -> ProbeResult:
    connector = ProxyConnector.from_url(proxy.url)
    client_timeout = ClientTimeout(total=timeout_sec)
    start = time.monotonic()
    try:
        async with ClientSession(
            connector=connector, timeout=client_timeout
        ) as session:
            async with session.get(target) as resp:
                elapsed = (time.monotonic() - start) * 1000
                remote_ip = None
                country = None
                try:
                    body = await resp.json(content_type=None)
                    remote_ip = _extract_ip(body)
                    country = _extract_country(body)
                except Exception:
                    pass
                return ProbeResult(
                    proxy=str(proxy),
                    success=resp.status == 200,
                    latency_ms=round(elapsed, 1),
                    status_code=resp.status,
                    remote_ip=remote_ip,
                    country=country,
                )
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return ProbeResult(
            proxy=str(proxy),
            success=False,
            latency_ms=round(elapsed, 1),
            error=type(e).__name__,
        )


async def benchmark_proxy(
    proxy: Proxy,
    target: str,
    rounds: int,
    timeout_sec: float,
    concurrency: int,
) -> BenchmarkResult:
    sem = asyncio.Semaphore(concurrency)

    async def limited_probe() -> ProbeResult:
        async with sem:
            return await probe_once(proxy, target, timeout_sec)

    tasks = [limited_probe() for _ in range(rounds)]
    results = await asyncio.gather(*tasks)

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    latencies = sorted(r.latency_ms for r in successful)
    ips = list({r.remote_ip for r in successful if r.remote_ip})

    errors: dict[str, int] = {}
    for r in failed:
        key = r.error or "unknown"
        errors[key] = errors.get(key, 0) + 1

    return BenchmarkResult(
        proxy=str(proxy),
        total_requests=len(results),
        successful=len(successful),
        failed=len(failed),
        success_rate=round(len(successful) / len(results) * 100, 1) if results else 0,
        latency_min_ms=round(latencies[0], 1) if latencies else 0,
        latency_max_ms=round(latencies[-1], 1) if latencies else 0,
        latency_avg_ms=round(sum(latencies) / len(latencies), 1) if latencies else 0,
        latency_p50_ms=round(_percentile(latencies, 50), 1),
        latency_p95_ms=round(_percentile(latencies, 95), 1),
        unique_ips=len(ips),
        ips=ips,
        errors=errors,
    )


async def test_rotation(
    proxy: Proxy,
    target: str,
    rounds: int,
    timeout_sec: float,
    concurrency: int,
) -> RotationResult:
    sem = asyncio.Semaphore(concurrency)

    async def limited_probe() -> ProbeResult:
        async with sem:
            return await probe_once(proxy, target, timeout_sec)

    tasks = [limited_probe() for _ in range(rounds)]
    results = await asyncio.gather(*tasks)

    successful = [r for r in results if r.success]
    all_ips = [r.remote_ip for r in successful if r.remote_ip]
    unique_ips = list(set(all_ips))

    countries: dict[str, int] = {}
    for r in successful:
        if r.country:
            countries[r.country] = countries.get(r.country, 0) + 1

    return RotationResult(
        proxy=str(proxy),
        total_requests=len(results),
        successful=len(successful),
        unique_ips=len(unique_ips),
        rotation_ratio=round(len(unique_ips) / len(successful) * 100, 1)
        if successful
        else 0,
        ips=unique_ips,
        country_distribution=countries,
    )
