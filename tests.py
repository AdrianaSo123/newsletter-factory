"""
Tests for the Newsletter Factory

Run with: python -m pytest tests.py
"""

from datetime import datetime
from newsletter_factory import NewsletterFactory, InvestmentStage
from models import Company, Investment, EntrepreneurTip, MarketTrend
from data_sources import MockDataSource
from sections import InvestmentHighlightsSection, ExecutiveSummarySection
from content_generator import EntrepreneurshipContentGenerator


def test_company_creation():
    """Test Company model"""
    company = Company(
        name="TestCo",
        description="A test company",
        sector="AI",
        website="https://test.co"
    )
    assert company.name == "TestCo"
    assert str(company) == "TestCo (AI)"


def test_investment_creation():
    """Test Investment model"""
    investor = Company("InvestorCo", "Investor", "VC Firm")
    investee = Company("StartupCo", "Startup", "AI")
    
    investment = Investment(
        investor=investor,
        investee=investee,
        amount=100.0,
        stage=InvestmentStage.SERIES_A,
        date=datetime.now(),
        details="Test investment"
    )
    
    assert investment.format_amount() == "$100.0M"
    assert "InvestorCo" in str(investment)


def test_mock_data_source():
    """Test MockDataSource returns data"""
    source = MockDataSource()
    investments = source.fetch_investments()
    
    assert len(investments) > 0
    assert all(isinstance(inv, Investment) for inv in investments)


def test_newsletter_factory_basic():
    """Test basic newsletter creation"""
    factory = NewsletterFactory(title="Test Newsletter")
    newsletter = factory.create()
    
    assert "Test Newsletter" in newsletter
    assert "202" in newsletter  # Should have a year


def test_newsletter_with_sections():
    """Test newsletter with sections"""
    source = MockDataSource()
    investments = source.fetch_investments()
    
    factory = NewsletterFactory()
    factory.add_section(InvestmentHighlightsSection(investments[:3]))
    
    newsletter = factory.create()
    assert "Investment Highlights" in newsletter


def test_content_generator():
    """Test content generation"""
    source = MockDataSource()
    investments = source.fetch_investments()
    
    gen = EntrepreneurshipContentGenerator()
    tips = gen.generate_tips_from_investments(investments)
    trends = gen.generate_market_trends(investments)
    
    assert len(tips) > 0
    assert len(trends) > 0
    assert all(isinstance(tip, EntrepreneurTip) for tip in tips)
    assert all(isinstance(trend, MarketTrend) for trend in trends)


def test_factory_reset():
    """Test factory reset functionality"""
    factory = NewsletterFactory()
    factory.add_section(ExecutiveSummarySection("Test", ["Item 1"]))
    
    assert len(factory.sections) == 1
    
    factory.reset()
    assert len(factory.sections) == 0


if __name__ == "__main__":
    # Run basic tests
    print("Running Newsletter Factory Tests...\n")
    
    tests = [
        ("Company Creation", test_company_creation),
        ("Investment Creation", test_investment_creation),
        ("Mock Data Source", test_mock_data_source),
        ("Newsletter Factory Basic", test_newsletter_factory_basic),
        ("Newsletter with Sections", test_newsletter_with_sections),
        ("Content Generator", test_content_generator),
        ("Factory Reset", test_factory_reset)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
