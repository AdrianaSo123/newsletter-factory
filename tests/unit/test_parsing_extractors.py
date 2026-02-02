from parsing.extractors import (
    parse_money_usd_millions,
    infer_stage,
    extract_company_name_from_title,
    extract_investor_names,
)
from newsletter_factory import InvestmentStage


def test_parse_money_millions_short():
    assert parse_money_usd_millions("Startup raises $12M") == 12.0


def test_parse_money_millions_long():
    assert parse_money_usd_millions("Startup raises $450 million") == 450.0


def test_parse_money_billions_short():
    assert parse_money_usd_millions("Startup raises $1.2B") == 1200.0


def test_parse_money_commas():
    assert parse_money_usd_millions("Startup raises $10,000M") == 10000.0


def test_parse_money_none():
    assert parse_money_usd_millions("No funding amount here") is None


def test_infer_stage_seed():
    assert infer_stage("seed round") == InvestmentStage.SEED


def test_infer_stage_series_b():
    assert infer_stage("Series B") == InvestmentStage.SERIES_B


def test_extract_company_name_from_title_conservative():
    assert extract_company_name_from_title("Acme AI raises $12M seed") == "Acme AI"


def test_extract_company_name_from_title_strips_exclusive_prefix():
    assert extract_company_name_from_title("Exclusive: Zocks Raises $45M Series B") == "Zocks"


def test_extract_investor_names_led_by():
    names = extract_investor_names("The round was led by Sequoia Capital, with participation from X.")
    assert "Sequoia Capital" in names
