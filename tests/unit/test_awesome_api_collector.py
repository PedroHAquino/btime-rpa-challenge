from decimal import Decimal
from unittest.mock import Mock

import pytest
import requests

from btime_rpa.infrastructure.api.awesome_api_collector import (
    AwesomeApiCollector,
)


def make_response(data=None, status_code=200, json_error=None):
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.json.return_value = data

    if json_error is not None:
        response.json.side_effect = json_error

    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"HTTP {status_code}"
        )
    else:
        response.raise_for_status.return_value = None

    return response


def make_session(response):
    session = Mock(spec=requests.Session)
    session.get.return_value = response
    return session


def test_collect_returns_two_exchange_rates():
    data = {
        "USDBRL": {"bid": "5.3716"},
        "EURBRL": {"bid": "6.0032"},
    }

    session = make_session(make_response(data))
    collector = AwesomeApiCollector(session=session)

    result = collector.collect()

    assert len(result) == 2
    assert result[0].currency == "USD"
    assert result[0].rate == Decimal("5.3716")
    assert result[1].currency == "EUR"
    assert result[1].rate == Decimal("6.0032")
    assert all(item.base_currency == "BRL" for item in result)
    assert all(item.source == "AwesomeAPI" for item in result)

    session.get.assert_called_once_with(
        AwesomeApiCollector.BASE_URL,
        timeout=15,
    )


def test_collect_rejects_missing_currency():
    data = {
        "USDBRL": {"bid": "5.3716"},
    }

    collector = AwesomeApiCollector(
        session=make_session(make_response(data))
    )

    with pytest.raises(ValueError, match="EURBRL"):
        collector.collect()


@pytest.mark.parametrize(
    "invalid_bid",
    ["inválido", None, ""],
)
def test_collect_rejects_invalid_bid(invalid_bid):
    data = {
        "USDBRL": {"bid": invalid_bid},
        "EURBRL": {"bid": "6.0032"},
    }

    collector = AwesomeApiCollector(
        session=make_session(make_response(data))
    )

    with pytest.raises(ValueError, match="Cotação inválida"):
        collector.collect()


def test_collect_rejects_invalid_json():
    response = make_response(
        json_error=ValueError("JSON inválido")
    )

    collector = AwesomeApiCollector(
        session=make_session(response)
    )

    with pytest.raises(ValueError, match="JSON inválido"):
        collector.collect()


def test_collect_handles_http_error():
    response = make_response(status_code=503)

    collector = AwesomeApiCollector(
        session=make_session(response)
    )

    with pytest.raises(RuntimeError, match="Falha ao consultar"):
        collector.collect()


def test_collect_handles_timeout():
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.Timeout("Tempo esgotado")

    collector = AwesomeApiCollector(session=session)

    with pytest.raises(RuntimeError, match="Falha ao consultar"):
        collector.collect()
