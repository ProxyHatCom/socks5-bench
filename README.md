# socks5-bench

Benchmark and health-check SOCKS5 proxies from the command line.

## Quick start

```bash
pip install git+https://github.com/ProxyHatCom/socks5-bench.git
socks5-bench run
```

The `run` command prompts for your proxy and runs all checks automatically. Paste a proxy in any common format:

```
socks5://user:pass@host:port
user:pass@host:port
host:port:user:pass
host:port
```

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
│ gate.example.com:1080│ OK     │  412ms  │ 74.89.46.126 │ US      │
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

If you route traffic through SOCKS5 proxies, you need answers to basic questions before putting them into production:

- **Are they alive?** Can the proxy connect and return a response?
- **How fast are they?** What's the p50/p95 latency under load?
- **Are they reliable?** What's the success rate over N requests?
- **Do they rotate?** How many unique IPs do you get across requests?

`socks5-bench` answers all of these in a single CLI tool. It works with **any SOCKS5 proxy provider**.

## Install

```bash
pip install git+https://github.com/ProxyHatCom/socks5-bench.git
```

Or clone and install locally:

```bash
git clone https://github.com/ProxyHatCom/socks5-bench.git
cd socks5-bench
pip install .
```

Or with Docker:

```bash
docker build -t socks5-bench .
docker run --rm socks5-bench check -p user:pass@proxy.example.com:1080
```

## Usage

### Interactive mode (easiest)

```bash
socks5-bench run
```

Prompts for proxy details, then runs health check, benchmark, and rotation test automatically.

### Health check

Verify proxies are alive and responding:

```bash
socks5-bench check -p user:pass@gate.example.com:1080
socks5-bench check -p proxy1.example.com:1080 -p proxy2.example.com:9050
socks5-bench check -c proxies.yaml
```

### Benchmark

Measure latency distribution and reliability over multiple requests:

```bash
socks5-bench bench -p user:pass@gate.example.com:1080 -n 20 -j 5
socks5-bench bench -c proxies.yaml --rounds 50 --concurrency 10
```

### Rotation test

Check how many unique IPs a rotating proxy returns:

```bash
socks5-bench rotate -p user:pass@gate.example.com:1080 -n 30
```

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--config` | `-c` | -- | Config file (YAML or JSON) |
| `--proxy` | `-p` | -- | Proxy as `host:port` or `user:pass@host:port` |
| `--target` | `-t` | `https://httpbin.org/ip` | URL to request through the proxy |
| `--rounds` | `-n` | 10 / 20 | Requests per proxy (bench / rotate) |
| `--concurrency` | `-j` | 3 / 5 | Concurrent requests (bench / rotate) |
| `--timeout` | | 10s | Request timeout |
| `--output` | `-o` | -- | Export results as JSON |

## Config file

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

## Metrics

| Metric | Description |
|--------|-------------|
| **Latency (avg / p50 / p95)** | Round-trip time through the proxy to the target URL. P50 is the median. P95 captures tail latency. |
| **Success rate** | Percentage of requests that returned HTTP 200. |
| **Unique IPs** | Number of distinct exit IPs observed. Static proxies should show 1. Rotating proxies should show more. |
| **Rotation ratio** | Unique IPs / successful requests. 100% means every request exited through a different IP. |

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
    "latency_min_ms": 198.3,
    "latency_max_ms": 312.4,
    "latency_avg_ms": 245.3,
    "latency_p50_ms": 238.1,
    "latency_p95_ms": 312.4,
    "unique_ips": 1,
    "ips": ["185.23.x.x"],
    "errors": {}
  }
]
```

## Example: ProxyHat configuration

This tool works with any SOCKS5 proxy provider. Here's an example using [ProxyHat](https://proxyhat.com/?utm_source=github&utm_medium=repo&utm_campaign=socks5-bench):

```yaml
proxies:
  - label: proxyhat-residential
    host: gate.proxyhat.com
    port: 1080
    username: your-username
    password: your-password
```

```bash
socks5-bench bench -c proxyhat.yaml -n 20 -j 5
```

## Development

```bash
git clone https://github.com/ProxyHatCom/socks5-bench.git
cd socks5-bench
pip install -e ".[dev]"
pytest
```

## License

MIT
