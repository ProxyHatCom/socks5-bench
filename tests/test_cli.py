from socks5_bench.cli import _try_parse_proxy_string


def test_parse_socks5_url_with_auth():
    p = _try_parse_proxy_string("socks5://user:pass@gate.example.com:1080")
    assert p.host == "gate.example.com"
    assert p.port == 1080
    assert p.username == "user"
    assert p.password == "pass"


def test_parse_socks5_url_no_auth():
    p = _try_parse_proxy_string("socks5://gate.example.com:1080")
    assert p.host == "gate.example.com"
    assert p.port == 1080
    assert p.username is None


def test_parse_user_pass_at_host_port():
    p = _try_parse_proxy_string("user:pass@proxy.example.com:1080")
    assert p.host == "proxy.example.com"
    assert p.port == 1080
    assert p.username == "user"
    assert p.password == "pass"


def test_parse_host_port_user_pass():
    p = _try_parse_proxy_string("proxy.example.com:1080:user:pass")
    assert p.host == "proxy.example.com"
    assert p.port == 1080
    assert p.username == "user"
    assert p.password == "pass"


def test_parse_host_port_only():
    p = _try_parse_proxy_string("proxy.example.com:1080")
    assert p.host == "proxy.example.com"
    assert p.port == 1080
    assert p.username is None
    assert p.password is None


def test_parse_with_whitespace():
    p = _try_parse_proxy_string("  socks5://user:pass@host.com:1080  ")
    assert p.host == "host.com"
    assert p.port == 1080


def test_parse_garbage_returns_none():
    assert _try_parse_proxy_string("not-a-proxy") is None
    assert _try_parse_proxy_string("") is None


def test_parse_complex_password_in_url():
    p = _try_parse_proxy_string("socks5://user:p@ss@gate.example.com:1080")
    assert p is not None
    assert p.host == "gate.example.com"
    assert p.port == 1080


def test_parse_long_username_with_dashes():
    p = _try_parse_proxy_string("abc123-country-us-sid-xyz:secretpass@gate.proxyhat.com:1080")
    assert p.host == "gate.proxyhat.com"
    assert p.port == 1080
    assert p.username == "abc123-country-us-sid-xyz"
    assert p.password == "secretpass"
