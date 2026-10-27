import csv
from pathlib import Path

from btime_rpa.application.use_cases.compare_exchange_rates import (
    CompareExchangeRates,
)
from btime_rpa.infrastructure.storage.csv_comparison_exporter import (
    CsvExchangeRateComparisonExporter,
)
from btime_rpa.infrastructure.storage.csv_reader import (
    CsvExchangeRateReader,
)


def test_comparison_workflow(tmp_path: Path) -> None:
    """Testa o fluxo completo de comparação entre API e scraping."""
    api_source = tmp_path / "api.csv"
    scraping_source = tmp_path / "scraping.csv"
    destination = tmp_path / "reports" / "comparison.csv"

    header = "currency,base_currency,rate,collected_at,source\n"
    collected_at = "2026-10-27T12:00:00+00:00"

    api_source.write_text(
        header
        + f"USD,BRL,5.30,{collected_at},AwesomeAPI\n"
        + f"EUR,BRL,6.00,{collected_at},AwesomeAPI\n",
        encoding="utf-8",
    )

    scraping_source.write_text(
        header
        + f"USD,BRL,5.35,{collected_at},Google Finance\n"
        + f"GBP,BRL,7.00,{collected_at},Google Finance\n",
        encoding="utf-8",
    )

    use_case = CompareExchangeRates(
        reader=CsvExchangeRateReader(),
    )

    result = use_case.execute(
        api_source=api_source,
        scraping_source=scraping_source,
    )

    CsvExchangeRateComparisonExporter().export(
        result,
        destination,
    )

    assert destination.is_file()

    with destination.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 3

    matched = next(
        row for row in rows if row["status"] == "MATCHED"
    )
    assert matched["currency"] == "USD"
    assert matched["api_rate"] == "5.30"
    assert matched["scraping_rate"] == "5.35"
    assert matched["absolute_difference"] == "0.05"
    assert matched["percentage_difference"] == "0.9434"

    missing_api = next(
        row for row in rows if row["status"] == "MISSING_IN_API"
    )
    assert missing_api["currency"] == "GBP"

    missing_scraping = next(
        row for row in rows if row["status"] == "MISSING_IN_SCRAPING"
    )
    assert missing_scraping["currency"] == "EUR"