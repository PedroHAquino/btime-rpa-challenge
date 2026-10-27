from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import requests

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_collector import ExchangeRateCollector


class AwesomeApiCollector(ExchangeRateCollector):
    BASE_URL = (
        "https://economia.awesomeapi.com.br/json/last/"
        "USD-BRL,EUR-BRL"
    )

    CURRENCIES = ("USD", "EUR")

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    def collect(self) -> list[ExchangeRate]:
        try:
            response = self.session.get(
                self.BASE_URL,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(
                "Falha ao consultar a AwesomeAPI"
            ) from exc
        except ValueError as exc:
            raise ValueError(
                "A AwesomeAPI retornou um JSON inválido"
            ) from exc

        exchange_rates = []

        for currency in self.CURRENCIES:
            pair = f"{currency}BRL"

            if not isinstance(data, dict) or pair not in data:
                raise ValueError(
                    f"Par de moedas ausente na API: {pair}"
                )

            try:
                rate = Decimal(str(data[pair]["bid"]))
            except (KeyError, TypeError, InvalidOperation) as exc:
                raise ValueError(
                    f"Cotação inválida na API: {pair}"
                ) from exc

            exchange_rates.append(
                ExchangeRate(
                    currency=currency,
                    base_currency="BRL",
                    rate=rate,
                    collected_at=datetime.now(UTC),
                    source="AwesomeAPI",
                )
            )

        return exchange_rates
