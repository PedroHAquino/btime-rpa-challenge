import csv
from unittest.mock import Mock

import requests

from btime_rpa.application.use_cases.collect_exchange_rates import (
    CollectExchangeRates,
)
from btime_rpa.infrastructure.api.awesome_api_collector import (
    AwesomeApiCollector,
)
from btime_rpa.infrastructure.storage.csv_exporter import (
    CsvExchangeRateExporter,
)


def test_api_workflow_generates_valid_csv(tmp_path):
    """Testa o fluxo completo da coleta via API até o CSV."""

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "USDBRL": {"bid": "5.3716"},
        "EURBRL": {"bid": "6.0302"},
    }

    session = Mock(spec=requests.Session)
    session.get.return_value = response

    use_case = CollectExchangeRates(
        collector=AwesomeApiCollector(session=session),
        exporter=CsvExchangeRateExporter(),
    )

    destination = tmp_path / "api_exchange_rates.csv"

    total = use_case.execute(destination)

    assert total == 2
    assert destination.exists()

    with destination.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert list(rows[0].keys()) == [
        "currency",
        "base_currency",
        "rate",
        "collected_at",
        "source",
    ]

    assert rows[0]["currency"] == "USD"
    assert rows[0]["base_currency"] == "BRL"
    assert rows[0]["rate"] == "5.3716"
    assert rows[0]["source"] == "AwesomeAPI"

    assert rows[1]["currency"] == "EUR"
    assert rows[1]["base_currency"] == "BRL"
    assert rows[1]["rate"] == "6.0302"
    assert rows[1]["source"] == "AwesomeAPI"

    session.get.assert_called_once_with(
        AwesomeApiCollector.BASE_URL,
        timeout=15,
    )
