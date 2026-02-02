from bs4 import BeautifulSoup

from scrapers.event_scrapers import EventbriteScraper


def _card(html: str):
    soup = BeautifulSoup(html, "lxml")
    return soup.find("div")


def test_eventbrite_does_not_invent_date_if_missing():
    scraper = EventbriteScraper(use_cache=False)
    card = _card(
        """
        <div class='discover-search-desktop-card'>
          <h3>Intro to AI</h3>
          <a href='https://example.com/event'>link</a>
          <p class='description'>Learn AI</p>
        </div>
        """
    )
    assert scraper._parse_event_card(card) is None


def test_eventbrite_filters_non_ai_events_even_on_ai_search_page():
    scraper = EventbriteScraper(use_cache=False)
    card = _card(
        """
        <div class='discover-search-desktop-card'>
          <h3>Skin Care Is a Billion-Dollar Industry</h3>
          <a href='https://example.com/event'>link</a>
          <time>March 3, 2026</time>
          <p class='description'>Legacy building for pharmacists</p>
        </div>
        """
    )
    assert scraper._parse_event_card(card) is None


def test_eventbrite_accepts_ai_event_with_parseable_date():
    scraper = EventbriteScraper(use_cache=False)
    card = _card(
        """
        <div class='discover-search-desktop-card'>
          <h3>Intro to AI for Beginners</h3>
          <a href='https://example.com/event'>link</a>
          <time>March 3, 2026</time>
          <p class='description'>Artificial intelligence fundamentals</p>
        </div>
        """
    )
    ev = scraper._parse_event_card(card)
    assert ev is not None
    assert ev.name == "Intro to AI for Beginners"
    assert ev.url == "https://example.com/event"
