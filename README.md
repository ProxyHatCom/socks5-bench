# socks5-bench

Benchmark and health-check SOCKS5 proxies from the command line.

## Why

If you route traffic through SOCKS5 proxies, you need answers to basic questions before putting them into production:

- **Are they alive?** Can the proxy connect and return a response?
- **How fast are they?** What's the p50/p95 latency under load?
- **Are they reliable?** What's the success rate over N requests?
- **Do they rotate?** How many unique IPs do you get across requests?

`socks5-bench` answers all of these in a single CLI tool. It works with **any SOCKS5 proxy provider**.

## Install

```bash
pip install .
```

Or with Docker:

```bash
docker build -t socks5-bench .
docker run --rm socks5-bench check -p user:pass@proxy.example.com:1080
```

## Usage

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

## Example output

### `socks5-bench check`

```
             Proxy Health Check
┌────────────────┬────────┬─────────┬─────────────────┬─────────┬───────┐
│ Proxy          │ Status │ Latency │ IP              │ Country │ Error │
├────────────────┼────────┼─────────┼─────────────────┼─────────┼───────┤
│ datacenter-1   │ OK     │  245ms  │ 185.23.x.x      │ --      │       │
│ residential-1  │ OK     │  891ms  │ 92.118.x.x      │ --      │       │
└────────────────┴────────┴─────────┴─────────────────┴─────────┴───────┘
```

### `socks5-bench bench`

```
                           Proxy Benchmark
┌────────────────┬─────────┬───────┬────────┬────────┬────────┬─────┬──────────────┐
│ Proxy          │ OK/Fail │  Rate │    Avg │    P50 │    P95 │ IPs │ Errors       │
├────────────────┼─────────┼───────┼────────┼────────┼────────┼─────┼──────────────┤
│ datacenter-1   │    10/0 │ 100%  │  245ms │  238ms │  312ms │   1 │              │
│ residential-1  │     9/1 │  90%  │  892ms │  845ms │ 1241ms │   3 │ TimeoutError │
└────────────────┴─────────┴───────┴────────┴────────┴────────┴─────┴──────────────┘
```

### `socks5-bench rotate`

```
                         IP Rotation Test
┌────────────────┬──────────┬────────────┬──────────┬──────────────────┐
│ Proxy          │ Requests │ Unique IPs │ Rotation │ Countries        │
├────────────────┼──────────┼────────────┼──────────┼──────────────────┤
│ residential-1  │    18/20 │         14 │    77.8% │ US(9), DE(5), …  │
└────────────────┴──────────┴────────────┴──────────┴──────────────────┘
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
pip install -e ".[dev]"
pytest
```

## License

MIT
