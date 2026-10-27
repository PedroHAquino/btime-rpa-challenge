from decimal import Decimal
from unittest.mock import Mock

import pytest
import requests

from btime_rpa.infrastructure.scraping.google_finance_collector import (
    GoogleFinanceCollector,
)


def make_response(html: str, status_code: int = 200):
    response = Mock(spec=requests.Response)
    response.text = html
    response.status_code = status_code
    response.raise_for_status.side_effect = (
        requests.HTTPError("Erro HTTP")
        if status_code >= 400
        else None
    )
    return response


def test_collect_returns_two_exchange_rates():
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.side_effect = [
        make_response('<div class="N6SYTe"><span jsname="Pdsbrc">5.3741</span></div>'),
        make_response('<div class="N6SYTe"><span jsname="Pdsbrc">6.0060</span></div>'),
    ]

    collector = GoogleFinanceCollector(session=session)
    result = collector.collect()

    assert len(result) == 2
    assert result[0].currency == "USD"
    assert result[0].rate == Decimal("5.3741")
    assert result[1].currency == "EUR"
    assert result[1].rate == Decimal("6.0060")
    assert all(item.base_currency == "BRL" for item in result)
    assert all(item.source == "Google Finance" for item in result)


def test_collect_raises_error_when_price_is_missing():
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.return_value = make_response("<html><body></body></html>")

    collector = GoogleFinanceCollector(session=session)

    with pytest.raises(ValueError, match="Cotação não encontrada"):
        collector.collect()


def test_collect_raises_error_when_price_is_invalid():
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.return_value = make_response(
        '<div class="N6SYTe"><span jsname="Pdsbrc">inválido</span></div>'
    )

    collector = GoogleFinanceCollector(session=session)

    with pytest.raises(ValueError, match="Cotação inválida"):
        collector.collect()


def test_collect_handles_http_error():
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.return_value = make_response("", status_code=403)

    collector = GoogleFinanceCollector(session=session)

    with pytest.raises(RuntimeError, match="Falha ao consultar Google Finance"):
        collector.collect()


def test_collect_handles_timeout():
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.side_effect = requests.Timeout("Tempo esgotado")

    collector = GoogleFinanceCollector(session=session)

    with pytest.raises(RuntimeError, match="Falha ao consultar Google Finance"):
        collector.collect()


def test_retry_configuration():
    collector = GoogleFinanceCollector()

    adapter = collector.session.get_adapter(
        "https://www.google.com/finance/quote/USD-BRL"
    )

    retry = adapter.max_retries

    assert retry.total == 3
    assert retry.connect == 3
    assert retry.read == 3
    assert retry.backoff_factor == 1
    assert retry.allowed_methods == frozenset({"GET"})
    assert retry.respect_retry_after_header is True


def test_retry_http_status_codes():
    collector = GoogleFinanceCollector()

    adapter = collector.session.get_adapter(
        "https://www.google.com/finance/quote/USD-BRL"
    )

    retry = adapter.max_retries

    assert 429 in retry.status_forcelist
    assert 503 in retry.status_forcelist
    assert 403 not in retry.status_forcelist


def test_retry_has_maximum_attempts():
    collector = GoogleFinanceCollector()

    adapter = collector.session.get_adapter(
        "https://www.google.com/finance/quote/USD-BRL"
    )

    retry = adapter.max_retries

    assert retry.total == 3
    assert retry.raise_on_status is False


def test_retry_repeats_request_after_http_503(monkeypatch):
    from io import BytesIO

    from urllib3.connectionpool import HTTPSConnectionPool
    from urllib3.response import HTTPResponse

    attempts = []

    def fake_make_request(self, conn, method, url, *args, **kwargs):
        attempts.append(method)

        status = 503 if len(attempts) < 3 else 200

        return HTTPResponse(
            body=BytesIO(b"<html>OK</html>"),
            status=status,
            headers={"Content-Type": "text/html"},
            preload_content=False,
        )

    monkeypatch.setattr(
        HTTPSConnectionPool,
        "_make_request",
        fake_make_request,
    )

    collector = GoogleFinanceCollector()

    # Evita esperas reais durante o teste de backoff.
    monkeypatch.setattr(
        "urllib3.util.retry.Retry.sleep",
        lambda self, response=None: None,
    )

    response = collector.session.get(
        "https://www.google.com/finance/quote/USD-BRL",
        timeout=5,
    )

    assert response.status_code == 200
    assert len(attempts) == 3
    assert attempts == ["GET", "GET", "GET"]


def test_retry_stops_after_maximum_attempts(monkeypatch):
    from io import BytesIO

    from urllib3.connectionpool import HTTPSConnectionPool
    from urllib3.response import HTTPResponse

    attempts = []

    def fake_make_request(self, conn, method, url, *args, **kwargs):
        attempts.append(method)

        return HTTPResponse(
            body=BytesIO(b"Service Unavailable"),
            status=503,
            headers={"Content-Type": "text/plain"},
            preload_content=False,
        )

    monkeypatch.setattr(
        HTTPSConnectionPool,
        "_make_request",
        fake_make_request,
    )

    monkeypatch.setattr(
        "urllib3.util.retry.Retry.sleep",
        lambda self, response=None: None,
    )

    collector = GoogleFinanceCollector()

    response = collector.session.get(
        "https://www.google.com/finance/quote/USD-BRL",
        timeout=5,
    )

    assert response.status_code == 503
    assert len(attempts) == 4
    assert attempts == ["GET"] * 4
