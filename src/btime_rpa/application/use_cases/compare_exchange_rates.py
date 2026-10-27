from pathlib import Path
from btime_rpa.domain.entities.comparison_result import ComparisonResult
from btime_rpa.domain.entities.exchange_rate_comparison import (
    ExchangeRateComparison,
)
from btime_rpa.domain.ports.exchange_rate_reader import ExchangeRateReader



class CompareExchangeRates:
    """Compara cotações obtidas por API e scraping."""

    def __init__(self, reader: ExchangeRateReader) -> None:
        self._reader = reader

    def execute(
        self,
        api_source: Path,
        scraping_source: Path,
    ) -> ComparisonResult:
        """Lê as duas fontes e compara os pares de moedas."""
        api_rates = self._reader.read(api_source)
        scraping_rates = self._reader.read(scraping_source)

        api_by_pair = {
            (rate.currency, rate.base_currency): rate
            for rate in api_rates
        }
        scraping_by_pair = {
            (rate.currency, rate.base_currency): rate
            for rate in scraping_rates
        }

        api_pairs = set(api_by_pair)
        scraping_pairs = set(scraping_by_pair)

        common_pairs = api_pairs & scraping_pairs

        comparisons = [
            ExchangeRateComparison(
                api_rate=api_by_pair[pair],
                scraping_rate=scraping_by_pair[pair],
            )
            for pair in sorted(common_pairs)
        ]

        missing_in_api = [
            f"{currency}/{base_currency}"
            for currency, base_currency in sorted(
                scraping_pairs - api_pairs
            )
        ]

        missing_in_scraping = [
            f"{currency}/{base_currency}"
            for currency, base_currency in sorted(
                api_pairs - scraping_pairs
            )
        ]

        return ComparisonResult(
            comparisons=comparisons,
            missing_in_api=missing_in_api,
            missing_in_scraping=missing_in_scraping,
        )