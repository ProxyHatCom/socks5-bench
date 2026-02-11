from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from socks5_bench.models import Proxy


def load_config(path: str) -> dict[str, Any]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def parse_proxies_from_config(config: dict[str, Any]) -> list[Proxy]:
    proxies = []
    for entry in config.get("proxies", []):
        proxies.append(
            Proxy(
                host=entry["host"],
                port=int(entry["port"]),
                username=entry.get("username"),
                password=entry.get("password"),
                label=entry.get("label"),
            )
        )
    return proxies


def parse_proxy_string(s: str) -> Proxy:
    if "@" in s:
        auth, hostport = s.rsplit("@", 1)
        username, password = auth.split(":", 1)
    else:
        hostport = s
        username = password = None
    host, port_str = hostport.rsplit(":", 1)
    return Proxy(host=host, port=int(port_str), username=username, password=password)
