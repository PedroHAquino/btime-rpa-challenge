from dataclasses import dataclass
from decimal import Decimal

from btime_rpa.domain.entities.exchange_rate import ExchangeRate


@dataclass(frozen=True, slots=True)
class ExchangeRateComparison:
    """Representa a comparação entre cotações de duas fontes."""

    api_rate: ExchangeRate
    scraping_rate: ExchangeRate

    def __post_init__(self) -> None:
        """Valida se as cotações representam o mesmo par de moedas."""
        if (
            self.api_rate.currency != self.scraping_rate.currency
            or self.api_rate.base_currency
            != self.scraping_rate.base_currency
        ):
            raise ValueError(
                "As cotações devem representar o mesmo par de moedas."
            )

    @property
    def absolute_difference(self) -> Decimal:
        """Retorna a diferença absoluta entre as cotações."""
        return abs(self.scraping_rate.rate - self.api_rate.rate)

    @property
    def percentage_difference(self) -> Decimal:
        """Retorna a diferença percentual em relação à API."""
        return (
            (self.scraping_rate.rate - self.api_rate.rate)
            / self.api_rate.rate
        ) * Decimal("100")