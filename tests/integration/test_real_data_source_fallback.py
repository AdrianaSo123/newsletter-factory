from scrapers.real_data_source import RealTimeDataSource


def test_real_data_source_falls_back_to_mock_on_failure(monkeypatch):
    # Force the aggregator to throw.
    def boom(*args, **kwargs):
        raise RuntimeError("scrape failed")

    ds = RealTimeDataSource(use_cache=True)
    monkeypatch.setattr(ds.aggregator, "fetch_recent_investments", boom, raising=True)

    investments = ds.fetch_investments(days_back=7)
    assert len(investments) > 0
