from socks5_bench.checker import _extract_ip, _extract_country, _percentile


def test_extract_ip_httpbin():
    assert _extract_ip({"origin": "1.2.3.4"}) == "1.2.3.4"


def test_extract_ip_ipapi():
    assert _extract_ip({"query": "5.6.7.8", "country": "US"}) == "5.6.7.8"


def test_extract_ip_generic():
    assert _extract_ip({"ip": "9.10.11.12"}) == "9.10.11.12"


def test_extract_ip_missing():
    assert _extract_ip({"data": "none"}) is None


def test_extract_country():
    assert _extract_country({"country": "Germany"}) == "Germany"
    assert _extract_country({"countryCode": "DE"}) == "DE"
    assert _extract_country({"ip": "1.2.3.4"}) is None


def test_percentile_empty():
    assert _percentile([], 50) == 0.0


def test_percentile_single():
    assert _percentile([100.0], 50) == 100.0
    assert _percentile([100.0], 95) == 100.0


def test_percentile_basic():
    data = sorted([10.0, 20.0, 30.0, 40.0, 50.0])
    assert _percentile(data, 0) == 10.0
    assert _percentile(data, 50) == 30.0
    assert _percentile(data, 100) == 50.0
