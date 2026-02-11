import json
import os
import tempfile

import yaml

from socks5_bench.config import load_config, parse_proxies_from_config, parse_proxy_string


def test_parse_proxy_with_auth():
    p = parse_proxy_string("user:pass@proxy.example.com:1080")
    assert p.host == "proxy.example.com"
    assert p.port == 1080
    assert p.username == "user"
    assert p.password == "pass"


def test_parse_proxy_without_auth():
    p = parse_proxy_string("proxy.example.com:1080")
    assert p.host == "proxy.example.com"
    assert p.port == 1080
    assert p.username is None
    assert p.password is None


def test_parse_proxy_complex_password():
    p = parse_proxy_string("user:p@ss:word@proxy.example.com:1080")
    assert p.username == "user"
    assert p.password == "p@ss:word"
    assert p.host == "proxy.example.com"
    assert p.port == 1080


def test_load_yaml_config():
    data = {
        "proxies": [
            {"host": "gate.example.com", "port": 1080, "username": "u", "password": "p", "label": "test"}
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.dump(data, f)
        path = f.name
    try:
        config = load_config(path)
        proxies = parse_proxies_from_config(config)
        assert len(proxies) == 1
        assert proxies[0].host == "gate.example.com"
        assert proxies[0].port == 1080
        assert proxies[0].label == "test"
    finally:
        os.unlink(path)


def test_load_json_config():
    data = {
        "proxies": [
            {"host": "proxy.example.com", "port": 9050}
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        path = f.name
    try:
        config = load_config(path)
        proxies = parse_proxies_from_config(config)
        assert len(proxies) == 1
        assert proxies[0].host == "proxy.example.com"
        assert proxies[0].username is None
    finally:
        os.unlink(path)


def test_parse_proxies_empty_config():
    proxies = parse_proxies_from_config({})
    assert proxies == []
