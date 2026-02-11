from socks5_bench.models import Proxy


def test_proxy_url_with_auth():
    p = Proxy(host="example.com", port=1080, username="user", password="pass")
    assert p.url == "socks5://user:pass@example.com:1080"


def test_proxy_url_without_auth():
    p = Proxy(host="example.com", port=1080)
    assert p.url == "socks5://example.com:1080"


def test_proxy_str_with_label():
    p = Proxy(host="example.com", port=1080, label="my-proxy")
    assert str(p) == "my-proxy"


def test_proxy_str_without_label():
    p = Proxy(host="example.com", port=1080)
    assert str(p) == "example.com:1080"
