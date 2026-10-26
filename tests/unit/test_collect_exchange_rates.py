
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock

import pytest

from btime_rpa.application.use_cases.collect_exchange_rates import (
    CollectExchangeRates,
)
from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_collector import (
    ExchangeRateCollector,
)
from btime_rpa.domain.ports.exchange_rate_exporter import (
    ExchangeRateExporter,
)


@pytest.fixture
def exchange_rates():
    return [
        ExchangeRate(
            currency="USD",
            base_currency="BRL",
            rate=Decimal("5.2450"),
            collected_at=datetime.now(timezone.utc),
            source="api",
        ),
        ExchangeRate(
            currency="EUR",
            base_currency="BRL",
            rate=Decimal("6.1500"),
            collected_at=datetime.now(timezone.utc),
            source="api",
        ),
    ]


@pytest.fixture
def collector():
    return Mock(spec=ExchangeRateCollector)


@pytest.fixture
def exporter():
    return Mock(spec=ExchangeRateExporter)


def test_collect_and_export_successfully(
    collector, exporter, exchange_rates
):
    collector.collect.return_value = exchange_rates

    use_case = CollectExchangeRates(collector, exporter)
    destination = Path("data/output/rates.csv")

    result = use_case.execute(destination)

    assert result == 2
    collector.collect.assert_called_once_with()
    exporter.export.assert_called_once_with(
        exchange_rates, destination
    )


def test_reject_empty_collection(collector, exporter):
    collector.collect.return_value = []

    use_case = CollectExchangeRates(collector, exporter)

    with pytest.raises(
        ValueError, match="Nenhuma cotação foi encontrada"
    ):
        use_case.execute(Path("data/output/rates.csv"))

    exporter.export.assert_not_called()


def test_propagate_collector_error(collector, exporter):
    collector.collect.side_effect = ConnectionError(
        "Falha na conexão"
    )

    use_case = CollectExchangeRates(collector, exporter)

    with pytest.raises(ConnectionError, match="Falha na conexão"):
        use_case.execute(Path("data/output/rates.csv"))

    exporter.export.assert_not_called()


def test_propagate_exporter_error(
    collector, exporter, exchange_rates
):
    collector.collect.return_value = exchange_rates
    exporter.export.side_effect = OSError(
        "Falha ao gravar arquivo"
    )

    use_case = CollectExchangeRates(collector, exporter)

    with pytest.raises(OSError, match="Falha ao gravar arquivo"):
        use_case.execute(Path("data/output/rates.csv"))

    collector.collect.assert_called_once_with()
    exporter.export.assert_called_once()
