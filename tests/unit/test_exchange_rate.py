
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from btime_rpa.domain.entities.exchange_rate import ExchangeRate


@pytest.fixture
def valid_data():
    return {
        "currency": "USD",
        "base_currency": "BRL",
        "rate": Decimal("5.2450"),
        "collected_at": datetime.now(timezone.utc),
        "source": "api",
    }


def test_create_valid_exchange_rate(valid_data):
    exchange_rate = ExchangeRate(**valid_data)

    assert exchange_rate.currency == "USD"
    assert exchange_rate.base_currency == "BRL"
    assert exchange_rate.rate == Decimal("5.2450")
    assert exchange_rate.source == "api"


@pytest.mark.parametrize(
    "invalid_rate",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_reject_invalid_rate(valid_data, invalid_rate):
    valid_data["rate"] = invalid_rate

    with pytest.raises(ValueError):
        ExchangeRate(**valid_data)


def test_reject_same_currency(valid_data):
    valid_data["base_currency"] = "USD"

    with pytest.raises(ValueError):
        ExchangeRate(**valid_data)


@pytest.mark.parametrize("field", ["currency", "base_currency", "source"])
def test_reject_empty_required_fields(valid_data, field):
    valid_data[field] = ""

    with pytest.raises(ValueError):
        ExchangeRate(**valid_data)


def test_reject_datetime_without_timezone(valid_data):
    valid_data["collected_at"] = datetime(2026, 10, 26, 12, 0)

    with pytest.raises(ValueError):
        ExchangeRate(**valid_data)


def test_exchange_rate_is_immutable(valid_data):
    exchange_rate = ExchangeRate(**valid_data)

    with pytest.raises(AttributeError):
        exchange_rate.rate = Decimal("6.00")
