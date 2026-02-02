from scrapers.base_scraper import CacheManager


def test_cache_manager_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.base_scraper.ScraperConfig.CACHE_DIR", tmp_path)
    cache = CacheManager(tmp_path)

    url = "https://example.com/page"
    payload = {"hello": "world"}

    cache.set(url, payload)
    out = cache.get(url, max_age_hours=999)
    assert out == payload


def test_cache_expired_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.base_scraper.ScraperConfig.CACHE_DIR", tmp_path)
    cache = CacheManager(tmp_path)

    url = "https://example.com/page"
    cache.set(url, "data")

    # Force expiry
    assert cache.get(url, max_age_hours=0) is None


def test_cache_manager_redacts_google_api_key(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.base_scraper.ScraperConfig.CACHE_DIR", tmp_path)
    cache = CacheManager(tmp_path)

    url = "https://example.com/page"
    leaked = "AI" + "za" + "Sy" + ("A" * 35)
    payload = {
        "google_maps_api_key": leaked,
        "nested": {"html": f"<script>var k='{leaked}'</script>"},
    }

    cache.set(url, payload)
    out = cache.get(url, max_age_hours=999)

    assert out["google_maps_api_key"] == "[REDACTED]"
    assert leaked not in out["nested"]["html"]
