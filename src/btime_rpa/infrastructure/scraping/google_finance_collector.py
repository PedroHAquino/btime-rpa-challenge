from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_collector import ExchangeRateCollector


class GoogleFinanceCollector(ExchangeRateCollector):
    """Coleta cotações de moedas a partir do Google Finance."""

    BASE_URL = "https://www.google.com/finance/quote"
    PRICE_SELECTOR = 'div.N6SYTe span[jsname="Pdsbrc"]'
    CURRENCIES = ("USD", "EUR")

    def __init__(self, session: requests.Session | None = None):
        """Configura a sessão HTTP e sua política de repetição."""
        self.session = session or requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
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
        """Extrai e normaliza cotações do HTML do Google Finance.

        Returns:
            Cotações de USD e EUR em relação ao BRL.

        Raises:
            RuntimeError: Se uma consulta HTTP falhar.
            ValueError: Se o preço não estiver presente ou for inválido.
        """
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
                    collected_at=datetime.now(UTC),
                    source="Google Finance",
                )
            )

        return exchange_rates
