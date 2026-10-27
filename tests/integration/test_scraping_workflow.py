import csv
from datetime import datetime
from unittest.mock import Mock

import requests

from btime_rpa.application.use_cases.collect_exchange_rates import (
    CollectExchangeRates,
)
from btime_rpa.infrastructure.scraping.google_finance_collector import (
    GoogleFinanceCollector,
)
from btime_rpa.infrastructure.storage.csv_exporter import (
    CsvExchangeRateExporter,
)


def test_scraping_workflow_generates_valid_csv(tmp_path):
    """Testa o fluxo completo do scraping até o arquivo CSV."""

    session = Mock(spec=requests.Session)
    session.headers = {}

    usd_response = Mock()
    usd_response.raise_for_status.return_value = None
    usd_response.text = """
        <html>
            <div class="N6SYTe">
                <span jsname="Pdsbrc">5.4148</span>
            </div>
        </html>
    """

    eur_response = Mock()
    eur_response.raise_for_status.return_value = None
    eur_response.text = """
        <html>
            <div class="N6SYTe">
                <span jsname="Pdsbrc">5.9867</span>
            </div>
        </html>
    """

    session.get.side_effect = [usd_response, eur_response]

    use_case = CollectExchangeRates(
        collector=GoogleFinanceCollector(session=session),
        exporter=CsvExchangeRateExporter(),
    )

    destination = tmp_path / "scraping_exchange_rates.csv"

    total = use_case.execute(destination)

    assert total == 2
    assert destination.exists()

    with destination.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert list(rows[0]) == [
        "currency",
        "base_currency",
        "rate",
        "collected_at",
        "source",
    ]

    assert rows[0]["currency"] == "USD"
    assert rows[0]["base_currency"] == "BRL"
    assert rows[0]["rate"] == "5.4148"
    assert rows[0]["source"] == "Google Finance"

    assert rows[1]["currency"] == "EUR"
    assert rows[1]["base_currency"] == "BRL"
    assert rows[1]["rate"] == "5.9867"
    assert rows[1]["source"] == "Google Finance"

    for row in rows:
        assert datetime.fromisoformat(row["collected_at"]).tzinfo is not None

    assert session.get.call_count == 2

    session.get.assert_any_call(
        f"{GoogleFinanceCollector.BASE_URL}/USD-BRL",
        timeout=15,
    )

    session.get.assert_any_call(
        f"{GoogleFinanceCollector.BASE_URL}/EUR-BRL",
        timeout=15,
    )
