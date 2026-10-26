from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from bs4 import BeautifulSoup

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_collector import ExchangeRateCollector



class GoogleFinanceCollector(ExchangeRateCollector):
    BASE_URL = "https://www.google.com/finance/quote"
    PRICE_SELECTOR = 'div.N6SYTe span[jsname="Pdsbrc"]'
    CURRENCIES = ("USD", "EUR")

    # def __init__(self, session: requests.Session | None = None):
    #     self.session = session or requests.Session()
    #     self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

        self.session.headers.update({
            "User-Agent": "BTimeRPAChallenge/1.0",
        })

        if session is None:
            retry_strategy = Retry(
                total=3,
                connect=3,
                read=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=frozenset({"GET"}),
                respect_retry_after_header=True,
                raise_on_status=False,
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)

            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)


    def collect(self) -> list[ExchangeRate]:
        exchange_rates = []

        for currency in self.CURRENCIES:
            url = f"{self.BASE_URL}/{currency}-BRL"

            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
            except requests.RequestException as exc:
                raise RuntimeError(
                    f"Falha ao consultar Google Finance: {currency}/BRL"
                ) from exc

            soup = BeautifulSoup(response.text, "lxml")
            price_element = soup.select_one(self.PRICE_SELECTOR)

            if price_element is None:
                raise ValueError(
                    f"Cotação não encontrada no HTML: {currency}/BRL"
                )

            price_text = price_element.get_text(strip=True)

            try:
                rate = Decimal(price_text.replace(",", ""))
            except InvalidOperation as exc:
                raise ValueError(
                    f"Cotação inválida para {currency}/BRL: {price_text}"
                ) from exc

            exchange_rates.append(
                ExchangeRate(
                    currency=currency,
                    base_currency="BRL",
                    rate=rate,
                    collected_at=datetime.now(timezone.utc),
                    source="Google Finance",
                )
            )

        return exchange_rates
