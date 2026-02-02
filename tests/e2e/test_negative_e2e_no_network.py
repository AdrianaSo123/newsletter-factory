import re

from scrapers.real_data_source import RealTimeDataSource
from scrapers.event_scrapers import EventAggregator
from newsletter_factory import NewsletterFactory
from sections import ExecutiveSummarySection, InvestmentHighlightsSection
from event_sections import UpcomingEventsSection


def test_negative_e2e_generation_without_network_uses_fallback(disable_network):
    # RealTimeDataSource should fall back to mock data if scraping fails.
    invs = RealTimeDataSource(use_cache=True).fetch_investments(days_back=7)

    # Event aggregator may return only curated conferences if network is blocked.
    events = EventAggregator().fetch_upcoming_events(days_ahead=90)

    out = (
        NewsletterFactory(title="E2E")
        .add_section(ExecutiveSummarySection("s", ["k"]))
        .add_section(InvestmentHighlightsSection(invs, max_items=3))
        .add_section(UpcomingEventsSection(events, max_items=3))
        .create()
    )

    assert "# E2E" in out
    assert "Investment Highlights" in out
    assert "Upcoming AI Events" in out
    # sanity: markdown header exists
    assert re.search(r"^# ", out, re.M) is not None
    # grounding: at least one rendered citation/source line
    assert "**Source:**" in out
