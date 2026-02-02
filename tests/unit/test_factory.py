from newsletter_factory import NewsletterFactory
from sections import ExecutiveSummarySection


def test_factory_generates_header_and_date():
    f = NewsletterFactory(title="Test")
    out = f.create()
    assert "# Test" in out
    assert "---" in out


def test_factory_builder_add_section_returns_self():
    f = NewsletterFactory()
    s = ExecutiveSummarySection("hello", ["a"]) 
    returned = f.add_section(s)
    assert returned is f
    assert len(f.sections) == 1


def test_factory_reset_clears_sections():
    f = NewsletterFactory()
    f.add_section(ExecutiveSummarySection("hello", ["a"]))
    f.reset()
    assert f.sections == []
