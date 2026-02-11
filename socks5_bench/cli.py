from __future__ import annotations

import asyncio
import re
from dataclasses import asdict

import click

from socks5_bench.checker import (
    DEFAULT_TARGET,
    GEO_TARGET,
    benchmark_proxy,
    probe_once,
    test_rotation,
)
from socks5_bench.config import load_config, parse_proxies_from_config, parse_proxy_string
from socks5_bench.models import Proxy
from socks5_bench.output import (
    console,
    export_json,
    print_benchmark_results,
    print_probe_results,
    print_rotation_results,
)


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


def _try_parse_proxy_string(raw: str) -> Proxy | None:
    """Try to parse a proxy from common formats. Returns None if not recognized."""
    raw = raw.strip()

    # socks5://user:pass@host:port or socks5://host:port
    m = re.match(r'^socks5?://(?:(.+?):(.+)@)?([^:@]+):(\d+)$', raw)
    if m:
        return Proxy(
            host=m.group(3), port=int(m.group(4)),
            username=m.group(1), password=m.group(2),
        )

    # user:pass@host:port
    m = re.match(r'^(.+?):(.+)@([^:@]+):(\d+)$', raw)
    if m:
        return Proxy(
            host=m.group(3), port=int(m.group(4)),
            username=m.group(1), password=m.group(2),
        )

    # host:port:user:pass
    m = re.match(r'^([^:]+):(\d+):(.+?):(.+)$', raw)
    if m:
        return Proxy(
            host=m.group(1), port=int(m.group(2)),
            username=m.group(3), password=m.group(4),
        )

    # host:port (no auth)
    m = re.match(r'^([^:]+):(\d+)$', raw)
    if m:
        return Proxy(host=m.group(1), port=int(m.group(2)))

    return None


@click.group(invoke_without_command=True)
@click.version_option(package_name="socks5-bench")
@click.pass_context
def main(ctx):
    """socks5-bench -- Benchmark and health-check SOCKS5 proxies."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


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


@main.command()
@click.option("--timeout", default=15.0, show_default=True, help="Request timeout in seconds.")
@click.option("--output", "-o", type=click.Path(), help="Export combined results to JSON.")
def run(timeout, output):
    """Interactive mode -- enter proxy details, run all checks."""
    console.print("\n[bold]socks5-bench[/bold] interactive mode\n")
    console.print(
        "[dim]  Paste a full proxy string or enter details manually.\n"
        "  Accepted formats:\n"
        "    socks5://user:pass@host:port\n"
        "    user:pass@host:port\n"
        "    host:port:user:pass\n"
        "    host:port[/dim]\n"
    )

    raw = click.prompt("  Proxy")
    proxy = _try_parse_proxy_string(raw)

    if proxy:
        auth_info = " (with auth)" if proxy.username else " (no auth)"
        console.print(f"  [green]Parsed:[/green] {proxy.host}:{proxy.port}{auth_info}")
    else:
        host = raw
        port = click.prompt("  Port", type=int, default=1080)
        auth = click.confirm("  Authentication required?", default=False)
        username = None
        password = None
        if auth:
            username = click.prompt("  Username")
            password = click.prompt("  Password", hide_input=True)
        proxy = Proxy(host=host, port=int(port), username=username, password=password)

    console.print(f"\n  Testing [cyan]{proxy.host}:{proxy.port}[/cyan] ...\n")

    # 1/3 Health check (with geo lookup)
    console.rule("[bold]1/3 Health Check")
    check_result = _run(probe_once(proxy, GEO_TARGET, timeout))
    print_probe_results([check_result])

    if not check_result.success:
        console.print("\n[red]Proxy failed health check. Aborting remaining tests.[/red]")
        raise SystemExit(1)

    # 2/3 Benchmark
    console.rule("[bold]2/3 Benchmark")
    console.print("[dim]  10 requests, concurrency 3[/dim]\n")
    bench_result = _run(benchmark_proxy(proxy, DEFAULT_TARGET, 10, timeout, 3))
    print_benchmark_results([bench_result])

    # 3/3 Rotation
    console.rule("[bold]3/3 IP Rotation")
    console.print("[dim]  20 requests, concurrency 5[/dim]\n")
    rotation_result = _run(test_rotation(proxy, DEFAULT_TARGET, 20, timeout, 5))
    print_rotation_results([rotation_result])

    console.print()

    if output:
        data = {
            "check": asdict(check_result),
            "benchmark": asdict(bench_result),
            "rotation": asdict(rotation_result),
        }
        export_json(output, data)
