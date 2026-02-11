from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from socks5_bench.models import BenchmarkResult, ProbeResult, RotationResult

console = Console()


def _fmt_latency(ms: float) -> str:
    if ms >= 1000:
        return f"{ms / 1000:.2f}s"
    return f"{ms:.0f}ms"


def print_probe_results(results: list[ProbeResult]) -> None:
    table = Table(title="Proxy Health Check")
    table.add_column("Proxy", style="cyan", no_wrap=True)
    table.add_column("Status")
    table.add_column("Latency", justify="right", no_wrap=True)
    table.add_column("IP", style="dim", no_wrap=True)
    table.add_column("Country", no_wrap=True)
    table.add_column("Error", style="red")

    for r in results:
        status = "[green]OK[/green]" if r.success else "[red]FAIL[/red]"
        latency = _fmt_latency(r.latency_ms) if r.success else "--"
        ip = r.remote_ip or "--"
        country = r.country or "--"
        error = r.error or ""
        table.add_row(r.proxy, status, latency, ip, country, error)

    console.print(table)


def print_benchmark_results(results: list[BenchmarkResult]) -> None:
    table = Table(title="Proxy Benchmark")
    table.add_column("Proxy", style="cyan", no_wrap=True)
    table.add_column("OK/Fail", justify="right", no_wrap=True)
    table.add_column("Rate", justify="right", no_wrap=True)
    table.add_column("Avg", justify="right", no_wrap=True)
    table.add_column("P50", justify="right", no_wrap=True)
    table.add_column("P95", justify="right", no_wrap=True)
    table.add_column("IPs", justify="right")
    table.add_column("Errors", style="red")

    for r in results:
        if r.success_rate >= 95:
            rate_style = "green"
        elif r.success_rate >= 80:
            rate_style = "yellow"
        else:
            rate_style = "red"

        errors = (
            ", ".join(f"{k}({v})" for k, v in r.errors.items())
            if r.errors
            else ""
        )
        table.add_row(
            r.proxy,
            f"{r.successful}/{r.failed}",
            f"[{rate_style}]{r.success_rate}%[/{rate_style}]",
            _fmt_latency(r.latency_avg_ms),
            _fmt_latency(r.latency_p50_ms),
            _fmt_latency(r.latency_p95_ms),
            str(r.unique_ips),
            errors,
        )

    console.print(table)

    for r in results:
        if r.ips:
            console.print(f"\n[dim]{r.proxy} IPs:[/dim] {', '.join(r.ips)}")


def print_rotation_results(results: list[RotationResult]) -> None:
    table = Table(title="IP Rotation Test")
    table.add_column("Proxy", style="cyan", no_wrap=True)
    table.add_column("Requests", justify="right", no_wrap=True)
    table.add_column("Unique IPs", justify="right", no_wrap=True)
    table.add_column("Rotation", justify="right", no_wrap=True)
    table.add_column("Countries")

    for r in results:
        if r.rotation_ratio >= 80:
            ratio_style = "green"
        elif r.rotation_ratio >= 50:
            ratio_style = "yellow"
        else:
            ratio_style = "red"

        countries = ", ".join(
            f"{k}({v})"
            for k, v in sorted(
                r.country_distribution.items(), key=lambda x: -x[1]
            )
        )
        table.add_row(
            r.proxy,
            f"{r.successful}/{r.total_requests}",
            str(r.unique_ips),
            f"[{ratio_style}]{r.rotation_ratio}%[/{ratio_style}]",
            countries or "--",
        )

    console.print(table)


def export_json(path: str, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
    console.print(f"\nResults exported to [bold]{path}[/bold]")
