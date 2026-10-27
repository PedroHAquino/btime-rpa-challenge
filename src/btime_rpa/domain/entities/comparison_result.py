from dataclasses import dataclass

from btime_rpa.domain.entities.exchange_rate_comparison import (
    ExchangeRateComparison,
)


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """Representa o resultado da comparação entre duas fontes."""

    comparisons: list[ExchangeRateComparison]
    missing_in_api: list[str]
    missing_in_scraping: list[str]