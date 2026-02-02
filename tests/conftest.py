import os
import pytest


@pytest.fixture(autouse=True)
def _set_test_env(tmp_path, monkeypatch):
    # Keep tests deterministic and avoid polluting real cache.
    monkeypatch.setenv("NEWSLETTER_FACTORY_TESTING", "1")
    monkeypatch.setenv("NEWSLETTER_FACTORY_CACHE_DIR", str(tmp_path / "cache"))


@pytest.fixture
def disable_network(monkeypatch):
    """Fail fast if a test accidentally makes real HTTP requests."""
    import requests

    def _blocked(*args, **kwargs):
        raise RuntimeError("Network disabled in tests; mock HTTP instead")

    monkeypatch.setattr(requests.Session, "get", _blocked, raising=True)
    return True
