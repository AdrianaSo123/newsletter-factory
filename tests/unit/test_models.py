from datetime import datetime

from newsletter_factory import InvestmentStage
from models import Company, Investment


def test_company_str():
    c = Company(name="Acme", description="d", sector="AI")
    assert str(c) == "Acme (AI)"


def test_investment_format_amount_millions():
    inv = Investment(
        investor=Company("VC", "d", "VC Firm"),
        investee=Company("Startup", "d", "LLM"),
        amount=12.3,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
    )
    assert inv.format_amount() == "$12.3M"


def test_investment_format_amount_billions():
    inv = Investment(
        investor=Company("VC", "d", "VC Firm"),
        investee=Company("Startup", "d", "LLM"),
        amount=2500.0,
        stage=InvestmentStage.SERIES_D_PLUS,
        date=datetime(2026, 2, 1),
    )
    assert inv.format_amount() == "$2.5B"
