<div align="center">

# socks5-bench

**Benchmark and health-check SOCKS5 proxies from the command line.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776ab.svg)](https://www.python.org)
[![SOCKS5](https://img.shields.io/badge/protocol-SOCKS5-48a9a6.svg)](#)

[Installation](#install) · [Usage](#usage) · [Options](#options) · [Config file](#config-file) · [JSON export](#json-export)

</div>

---

One command. Paste a proxy. Get latency stats, success rates, and IP rotation metrics.

```
$ socks5-bench run

socks5-bench interactive mode

  Paste a full proxy string or enter details manually.
  Accepted formats:
    socks5://user:pass@host:port
    user:pass@host:port
    host:port:user:pass
    host:port

  Proxy: user:pass@gate.example.com:1080
  Parsed: gate.example.com:1080 (with auth)

  Testing gate.example.com:1080 ...

──────────────────── 1/3 Health Check ─────────────────────
                    Proxy Health Check
┌──────────────────────┬────────┬─────────┬──────────────┬─────────┐
│ Proxy                │ Status │ Latency │ IP           │ Country │
├──────────────────────┼────────┼─────────┼──────────────┼─────────┤
│ gate.example.com:1080│ OK     │   412ms │ 74.89.46.126 │ US      │
└──────────────────────┴────────┴─────────┴──────────────┴─────────┘

───────────────────── 2/3 Benchmark ───────────────────────
  10 requests, concurrency 3

                       Proxy Benchmark
┌──────────────────────┬─────────┬───────┬───────┬───────┬───────┬─────┐
│ Proxy                │ OK/Fail │  Rate │   Avg │   P50 │   P95 │ IPs │
├──────────────────────┼─────────┼───────┼───────┼───────┼───────┼─────┤
│ gate.example.com:1080│    10/0 │ 100%  │ 438ms │ 425ms │ 512ms │   1 │
└──────────────────────┴─────────┴───────┴───────┴───────┴───────┴─────┘

──────────────────── 3/3 IP Rotation ──────────────────────
  20 requests, concurrency 5

                      IP Rotation Test
┌──────────────────────┬──────────┬────────────┬──────────┬───────────┐
│ Proxy                │ Requests │ Unique IPs │ Rotation │ Countries │
├──────────────────────┼──────────┼────────────┼──────────┼───────────┤
│ gate.example.com:1080│    20/20 │         16 │    80.0% │ US(20)    │
└──────────────────────┴──────────┴────────────┴──────────┴───────────┘
```

## Why

If you route traffic through SOCKS5 proxies you need answers before putting them into production:

- **Are they alive?** Can the proxy connect and return a response?
- **How fast?** What's the p50 / p95 latency under concurrent load?
- **Are they reliable?** What's the success rate over N requests?
- **Do they rotate?** How many unique exit IPs do you get?

`socks5-bench` answers all four in one tool. Works with **any SOCKS5 provider** — no vendor lock-in.

## Install

**macOS**

```bash
brew install pipx && pipx install git+https://github.com/ProxyHatCom/socks5-bench.git
```

**Linux**

```bash
python3 -m pip install pipx && pipx install git+https://github.com/ProxyHatCom/socks5-bench.git
```

**Windows**

```bash
pip install git+https://github.com/ProxyHatCom/socks5-bench.git
```

**Docker**

```bash
docker build -t socks5-bench .
docker run --rm -it socks5-bench run
```

> After install the `socks5-bench` command is available globally — no venv needed.

## Usage

### Interactive mode

The fastest way to test a proxy. Paste it in any format, the tool does the rest:

```bash
socks5-bench run
```

Runs health check → benchmark → IP rotation test in sequence.

### Health check

Verify proxies are alive and responding:

```bash
socks5-bench check -p user:pass@gate.example.com:1080
socks5-bench check -p proxy1.example.com:1080 -p proxy2.example.com:9050
socks5-bench check -c proxies.yaml
```

### Benchmark

Measure latency distribution and reliability under load:

```bash
socks5-bench bench -p user:pass@gate.example.com:1080 -n 20 -j 5
socks5-bench bench -c proxies.yaml --rounds 50 --concurrency 10
```

### Rotation test

Count unique exit IPs across requests:

```bash
socks5-bench rotate -p user:pass@gate.example.com:1080 -n 30
```

## Options

| Flag | Short | Default | Description |
|---|---|---|---|
| `--proxy` | `-p` | — | Proxy as `host:port` or `user:pass@host:port` |
| `--config` | `-c` | — | Config file (YAML or JSON) |
| `--target` | `-t` | `httpbin.org/ip` | URL to request through the proxy |
| `--rounds` | `-n` | `10` / `20` | Requests per proxy (bench / rotate) |
| `--concurrency` | `-j` | `3` / `5` | Parallel requests (bench / rotate) |
| `--timeout` | | `10s` | Per-request timeout |
| `--output` | `-o` | — | Export results to JSON file |

## Config file

Test multiple proxies from a YAML or JSON file:

```yaml
proxies:
  - label: datacenter-1
    host: gate.example.com
    port: 1080
    username: user
    password: pass

  - label: residential-1
    host: res.example.com
    port: 1080
    username: user
    password: pass
```

```bash
socks5-bench bench -c proxies.yaml -n 20 -j 5
```

## Metrics

| Metric | What it tells you |
|---|---|
| **Avg / P50 / P95 latency** | Round-trip time through the proxy. P50 = median, P95 = tail latency. |
| **Success rate** | Percentage of requests that returned HTTP 200. |
| **Unique IPs** | Distinct exit IPs observed. Static proxies → 1. Rotating → more. |
| **Rotation ratio** | Unique IPs ÷ successful requests. 100% = every request used a different IP. |

## JSON export

```bash
socks5-bench bench -c proxies.yaml -o results.json
```

```json
[
  {
    "proxy": "datacenter-1",
    "total_requests": 10,
    "successful": 10,
    "failed": 0,
    "success_rate": 100.0,
    "latency_avg_ms": 245.3,
    "latency_p50_ms": 238.1,
    "latency_p95_ms": 312.4,
    "unique_ips": 1,
    "ips": ["185.23.x.x"],
    "errors": {}
  }
]
```

## Provider example

This tool is provider-agnostic. Here's a sample config using [ProxyHat](https://proxyhat.com/?utm_source=github&utm_medium=repo&utm_campaign=socks5-bench):

```yaml
proxies:
  - label: proxyhat-residential
    host: gate.proxyhat.com
    port: 1080
    username: your-username
    password: your-password
```

## Development

```bash
git clone https://github.com/ProxyHatCom/socks5-bench.git
cd socks5-bench
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
