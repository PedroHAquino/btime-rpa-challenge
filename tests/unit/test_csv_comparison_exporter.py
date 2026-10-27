import csv
from datetime import datetime, timezone
from decimal import Decimal

from btime_rpa.domain.entities.comparison_result import ComparisonResult
from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.entities.exchange_rate_comparison import (
    ExchangeRateComparison,
)
from btime_rpa.infrastructure.storage.csv_comparison_exporter import (
    CsvExchangeRateComparisonExporter,
)


def make_rate(rate: str, source: str) -> ExchangeRate:
    """Cria uma cotação válida para os testes."""
    return ExchangeRate(
        currency="USD",
        base_currency="BRL",
        rate=Decimal(rate),
        collected_at=datetime(
            2026, 10, 27, 12, 0, tzinfo=timezone.utc
        ),
        source=source,
    )


def test_exports_matched_comparison(tmp_path) -> None:
    """Exporta corretamente as diferenças entre duas cotações."""
    result = ComparisonResult(
        comparisons=[
            ExchangeRateComparison(
                api_rate=make_rate("100", "AwesomeAPI"),
                scraping_rate=make_rate("105", "Google Finance"),
            )
        ],
        missing_in_api=[],
        missing_in_scraping=[],
    )

    destination = tmp_path / "reports" / "comparison.csv"

    CsvExchangeRateComparisonExporter().export(result, destination)

    with destination.open(
        encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["currency"] == "USD"
    assert rows[0]["base_currency"] == "BRL"
    assert rows[0]["api_rate"] == "100"
    assert rows[0]["scraping_rate"] == "105"
    assert rows[0]["absolute_difference"] == "5"
    assert rows[0]["percentage_difference"] == "5.0000"
    assert rows[0]["status"] == "MATCHED"
    assert rows[0]["api_collected_at"]
    assert rows[0]["scraping_collected_at"]


def test_exports_missing_currency_pairs(tmp_path) -> None:
    """Exporta os pares ausentes em cada fonte."""
    result = ComparisonResult(
        comparisons=[],
        missing_in_api=["GBP/BRL"],
        missing_in_scraping=["EUR/BRL"],
    )

    destination = tmp_path / "comparison.csv"

    CsvExchangeRateComparisonExporter().export(result, destination)

    with destination.open(
        encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["currency"] == "GBP"
    assert rows[0]["status"] == "MISSING_IN_API"
    assert rows[0]["api_rate"] == ""

    assert rows[1]["currency"] == "EUR"
    assert rows[1]["status"] == "MISSING_IN_SCRAPING"
    assert rows[1]["scraping_rate"] == ""


def test_exports_empty_report_with_header(tmp_path) -> None:
    """Gera o cabeçalho mesmo sem cotações."""
    result = ComparisonResult(
        comparisons=[],
        missing_in_api=[],
        missing_in_scraping=[],
    )

    destination = tmp_path / "comparison.csv"

    CsvExchangeRateComparisonExporter().export(result, destination)

    with destination.open(
        encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        assert reader.fieldnames is not None
        assert "percentage_difference" in reader.fieldnames
        assert "status" in reader.fieldnames

    assert rows == []