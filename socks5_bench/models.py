from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proxy:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    label: Optional[str] = None

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"socks5://{auth}{self.host}:{self.port}"

    def __str__(self) -> str:
        return self.label or f"{self.host}:{self.port}"


@dataclass
class ProbeResult:
    proxy: str
    success: bool
    latency_ms: float
    status_code: Optional[int] = None
    remote_ip: Optional[str] = None
    country: Optional[str] = None
    error: Optional[str] = None


@dataclass
class BenchmarkResult:
    proxy: str
    total_requests: int
    successful: int
    failed: int
    success_rate: float
    latency_min_ms: float
    latency_max_ms: float
    latency_avg_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    unique_ips: int
    ips: list[str] = field(default_factory=list)
    errors: dict[str, int] = field(default_factory=dict)


@dataclass
class RotationResult:
    proxy: str
    total_requests: int
    successful: int
    unique_ips: int
    rotation_ratio: float
    ips: list[str] = field(default_factory=list)
    country_distribution: dict[str, int] = field(default_factory=dict)
