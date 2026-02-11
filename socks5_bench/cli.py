from __future__ import annotations

import asyncio
from dataclasses import asdict

import click

from socks5_bench.checker import (
    DEFAULT_TARGET,
    benchmark_proxy,
    probe_once,
    test_rotation,
)
from socks5_bench.config import load_config, parse_proxies_from_config, parse_proxy_string
from socks5_bench.models import Proxy
from socks5_bench.output import console, export_json, print_benchmark_results, print_probe_results, print_rotation_results


def _resolve_proxies(
    config_path: str | None, proxy_args: tuple[str, ...]
) -> list[Proxy]:
    proxies: list[Proxy] = []
    if config_path:
        config = load_config(config_path)
        proxies.extend(parse_proxies_from_config(config))
    for p in proxy_args:
        proxies.append(parse_proxy_string(p))
    return proxies


def _run(coro):
    return asyncio.run(coro)


@click.group()
@click.version_option(package_name="socks5-bench")
def main():
    """socks5-bench -- Benchmark and health-check SOCKS5 proxies."""


@main.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file (YAML/JSON).")
@click.option("--proxy", "-p", multiple=True, help="Proxy as host:port or user:pass@host:port.")
@click.option("--target", "-t", default=DEFAULT_TARGET, show_default=True, help="Target URL for probing.")
@click.option("--timeout", default=10.0, show_default=True, help="Request timeout in seconds.")
@click.option("--output", "-o", type=click.Path(), help="Export results to JSON.")
def check(config, proxy, target, timeout, output):
    """Quick health check -- verify proxies are alive."""
    proxies = _resolve_proxies(config, proxy)
    if not proxies:
        console.print("[red]No proxies specified. Use --proxy or --config.[/red]")
        raise SystemExit(1)

    async def run():
        return await asyncio.gather(*[probe_once(p, target, timeout) for p in proxies])

    results = _run(run())
    print_probe_results(results)
    if output:
        export_json(output, [asdict(r) for r in results])


@main.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file (YAML/JSON).")
@click.option("--proxy", "-p", multiple=True, help="Proxy as host:port or user:pass@host:port.")
@click.option("--target", "-t", default=DEFAULT_TARGET, show_default=True, help="Target URL.")
@click.option("--rounds", "-n", default=10, show_default=True, help="Requests per proxy.")
@click.option("--concurrency", "-j", default=3, show_default=True, help="Concurrent requests per proxy.")
@click.option("--timeout", default=10.0, show_default=True, help="Request timeout in seconds.")
@click.option("--output", "-o", type=click.Path(), help="Export results to JSON.")
def bench(config, proxy, target, rounds, concurrency, timeout, output):
    """Benchmark proxy latency and reliability."""
    proxies = _resolve_proxies(config, proxy)
    if not proxies:
        console.print("[red]No proxies specified. Use --proxy or --config.[/red]")
        raise SystemExit(1)

    async def run():
        return await asyncio.gather(
            *[benchmark_proxy(p, target, rounds, timeout, concurrency) for p in proxies]
        )

    results = _run(run())
    print_benchmark_results(results)
    if output:
        export_json(output, [asdict(r) for r in results])


@main.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file (YAML/JSON).")
@click.option("--proxy", "-p", multiple=True, help="Proxy as host:port or user:pass@host:port.")
@click.option("--target", "-t", default=DEFAULT_TARGET, show_default=True, help="Target URL.")
@click.option("--rounds", "-n", default=20, show_default=True, help="Requests per proxy.")
@click.option("--concurrency", "-j", default=5, show_default=True, help="Concurrent requests per proxy.")
@click.option("--timeout", default=10.0, show_default=True, help="Request timeout in seconds.")
@click.option("--output", "-o", type=click.Path(), help="Export results to JSON.")
def rotate(config, proxy, target, rounds, concurrency, timeout, output):
    """Test IP rotation -- measure unique IPs across requests."""
    proxies = _resolve_proxies(config, proxy)
    if not proxies:
        console.print("[red]No proxies specified. Use --proxy or --config.[/red]")
        raise SystemExit(1)

    async def run():
        return await asyncio.gather(
            *[test_rotation(p, target, rounds, timeout, concurrency) for p in proxies]
        )

    results = _run(run())
    print_rotation_results(results)
    if output:
        export_json(output, [asdict(r) for r in results])
