from datetime import datetime, timezone
from decimal import Decimal

import pytest

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.entities.exchange_rate_comparison import (
    ExchangeRateComparison,
)


def make_exchange_rate(
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


def test_calculates_absolute_difference() -> None:
    """Verifica o cálculo da diferença absoluta."""
    comparison = ExchangeRateComparison(
        api_rate=make_exchange_rate("USD", "5.3441", "AwesomeAPI"),
        scraping_rate=make_exchange_rate(
            "USD", "5.3459", "Google Finance"
        ),
    )

    assert comparison.absolute_difference == Decimal("0.0018")


def test_calculates_percentage_difference() -> None:
    """Verifica a diferença percentual usando a API como referência."""
    comparison = ExchangeRateComparison(
        api_rate=make_exchange_rate("USD", "100", "AwesomeAPI"),
        scraping_rate=make_exchange_rate(
            "USD", "105", "Google Finance"
        ),
    )

    assert comparison.percentage_difference == Decimal("5")


def test_calculates_negative_percentage_difference() -> None:
    """Verifica diferenças percentuais negativas."""
    comparison = ExchangeRateComparison(
        api_rate=make_exchange_rate("USD", "100", "AwesomeAPI"),
        scraping_rate=make_exchange_rate(
            "USD", "95", "Google Finance"
        ),
    )

    assert comparison.percentage_difference == Decimal("-5")


def test_rejects_different_currency_pairs() -> None:
    """Impede a comparação de moedas diferentes."""
    with pytest.raises(ValueError, match="mesmo par de moedas"):
        ExchangeRateComparison(
            api_rate=make_exchange_rate(
                "USD", "5.3441", "AwesomeAPI"
            ),
            scraping_rate=make_exchange_rate(
                "EUR", "5.9590", "Google Finance"
            ),
        )