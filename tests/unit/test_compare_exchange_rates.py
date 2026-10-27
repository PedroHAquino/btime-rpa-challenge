from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

from btime_rpa.application.use_cases.compare_exchange_rates import (
    CompareExchangeRates,
)
from btime_rpa.domain.entities.exchange_rate import ExchangeRate


def make_rate(
    currency: str,
    rate: str,
    source: str,
) -> ExchangeRate:
    """Cria uma cotação válida para os testes."""
    return ExchangeRate(
        currency=currency,
        base_currency="BRL",
        rate=Decimal(rate),
        collected_at=datetime.now(timezone.utc),
        source=source,
    )


def test_compares_matching_currency_pairs() -> None:
    """Compara corretamente os pares presentes nas duas fontes."""
    api_path = Path("api.csv")
    scraping_path = Path("scraping.csv")

    reader = Mock()
    reader.read.side_effect = [
        [
            make_rate("USD", "5.30", "AwesomeAPI"),
            make_rate("EUR", "6.00", "AwesomeAPI"),
        ],
        [
            make_rate("USD", "5.35", "Google Finance"),
            make_rate("EUR", "6.06", "Google Finance"),
        ],
    ]

    result = CompareExchangeRates(reader).execute(
        api_path, scraping_path
    )

    assert len(result.comparisons) == 2
    assert result.comparisons[0].api_rate.currency == "EUR"
    assert result.comparisons[1].api_rate.currency == "USD"
    assert result.comparisons[1].absolute_difference == Decimal("0.05")
    assert result.missing_in_api == []
    assert result.missing_in_scraping == []

    assert reader.read.call_count == 2


def test_identifies_missing_currencies() -> None:
    """Identifica moedas ausentes em cada fonte."""
    reader = Mock()
    reader.read.side_effect = [
        [
            make_rate("USD", "5.30", "AwesomeAPI"),
            make_rate("EUR", "6.00", "AwesomeAPI"),
        ],
        [
            make_rate("USD", "5.35", "Google Finance"),
            make_rate("GBP", "7.00", "Google Finance"),
        ],
    ]

    result = CompareExchangeRates(reader).execute(
        Path("api.csv"),
        Path("scraping.csv"),
    )

    assert len(result.comparisons) == 1
    assert result.missing_in_api == ["GBP/BRL"]
    assert result.missing_in_scraping == ["EUR/BRL"]


def test_returns_empty_comparisons_when_no_pairs_match() -> None:
    """Retorna resultado sem comparações quando não há pares comuns."""
    reader = Mock()
    reader.read.side_effect = [
        [make_rate("USD", "5.30", "AwesomeAPI")],
        [make_rate("EUR", "6.00", "Google Finance")],
    ]

    result = CompareExchangeRates(reader).execute(
        Path("api.csv"),
        Path("scraping.csv"),
    )

    assert result.comparisons == []
    assert result.missing_in_api == ["EUR/BRL"]
    assert result.missing_in_scraping == ["USD/BRL"]


def test_handles_empty_sources() -> None:
    """Trata corretamente duas fontes sem cotações."""
    reader = Mock()
    reader.read.side_effect = [[], []]

    result = CompareExchangeRates(reader).execute(
        Path("api.csv"),
        Path("scraping.csv"),
    )

    assert result.comparisons == []
    assert result.missing_in_api == []
    assert result.missing_in_scraping == []