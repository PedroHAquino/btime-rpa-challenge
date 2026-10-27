
import csv
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.infrastructure.storage.csv_exporter import (
    CsvExchangeRateExporter,
)


@pytest.fixture
def exchange_rates():
    collected_at = datetime(
        2026, 10, 26, 20, 0, tzinfo=UTC
    )

    return [
        ExchangeRate(
            currency="USD",
            base_currency="BRL",
            rate=Decimal("5.2450"),
            collected_at=collected_at,
            source="api",
        ),
        ExchangeRate(
            currency="EUR",
            base_currency="BRL",
            rate=Decimal("6.1500"),
            collected_at=collected_at,
            source="api",
        ),
    ]


def test_export_creates_csv_with_correct_data(
    tmp_path, exchange_rates
):
    destination = tmp_path / "rates.csv"
    exporter = CsvExchangeRateExporter()

    exporter.export(exchange_rates, destination)

    assert destination.exists()

    with destination.open(
        encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["currency"] == "USD"
    assert rows[0]["base_currency"] == "BRL"
    assert rows[0]["rate"] == "5.2450"
    assert rows[0]["source"] == "api"
    assert rows[1]["currency"] == "EUR"


def test_export_preserves_decimal_precision(tmp_path):
    destination = tmp_path / "rates.csv"
    exporter = CsvExchangeRateExporter()

    rate = ExchangeRate(
        currency="USD",
        base_currency="BRL",
        rate=Decimal("5.123456789"),
        collected_at=datetime.now(UTC),
        source="api",
    )

    exporter.export([rate], destination)

    with destination.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["rate"] == "5.123456789"


def test_export_creates_missing_directories(
    tmp_path, exchange_rates
):
    destination = tmp_path / "nested" / "output" / "rates.csv"

    CsvExchangeRateExporter().export(
        exchange_rates, destination
    )

    assert destination.exists()


def test_export_writes_header_for_empty_list(tmp_path):
    destination = tmp_path / "empty.csv"

    CsvExchangeRateExporter().export([], destination)

    with destination.open(
        encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.reader(file))

    assert rows == [
        [
            "currency",
            "base_currency",
            "rate",
            "collected_at",
            "source",
        ]
    ]


def test_export_preserves_iso_datetime(
    tmp_path, exchange_rates
):
    destination = tmp_path / "rates.csv"

    CsvExchangeRateExporter().export(
        exchange_rates, destination
    )

    with destination.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert (
        rows[0]["collected_at"]
        == "2026-10-26T20:00:00+00:00"
    )


def test_export_raises_error_for_invalid_destination(
    tmp_path, exchange_rates
):
    destination = tmp_path / "existing_directory"
    destination.mkdir()

    with pytest.raises(OSError):
        CsvExchangeRateExporter().export(
            exchange_rates, destination
        )
