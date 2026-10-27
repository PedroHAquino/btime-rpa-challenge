import csv
from pathlib import Path

from btime_rpa.domain.entities.comparison_result import ComparisonResult
from btime_rpa.domain.ports.exchange_rate_comparison_exporter import (
    ExchangeRateComparisonExporter,
)
from decimal import Decimal

class CsvExchangeRateComparisonExporter(ExchangeRateComparisonExporter):
    """Exporta comparações de cotações para CSV."""

    FIELDNAMES = (
        "currency",
        "base_currency",
        "api_rate",
        "scraping_rate",
        "absolute_difference",
        "percentage_difference",
        "api_collected_at",
        "scraping_collected_at",
        "status",
    )

    def export(
        self,
        result: ComparisonResult,
        destination: Path,
    ) -> None:
        """Exporta comparações e identifica pares ausentes."""
        destination.parent.mkdir(parents=True, exist_ok=True)

        with destination.open(
            mode="w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )
            writer.writeheader()

            for comparison in result.comparisons:
                writer.writerow(
                    {
                        "currency": comparison.api_rate.currency,
                        "base_currency": comparison.api_rate.base_currency,
                        "api_rate": str(comparison.api_rate.rate),
                        "scraping_rate": str(comparison.scraping_rate.rate),
                        "absolute_difference": str(
                            comparison.absolute_difference
                        ),
                        "percentage_difference": str(
                            comparison.percentage_difference.quantize(
                                Decimal("0.0001")
                            )
                        ),
                        "api_collected_at": (
                            comparison.api_rate.collected_at.isoformat()
                        ),
                        "scraping_collected_at": (
                            comparison.scraping_rate.collected_at.isoformat()
                        ),
                        "status": "MATCHED",
                    }
                )

            for pair in result.missing_in_api:
                currency, base_currency = pair.split("/")
                writer.writerow(
                    {
                        "currency": currency,
                        "base_currency": base_currency,
                        "status": "MISSING_IN_API",
                    }
                )

            for pair in result.missing_in_scraping:
                currency, base_currency = pair.split("/")
                writer.writerow(
                    {
                        "currency": currency,
                        "base_currency": base_currency,
                        "status": "MISSING_IN_SCRAPING",
                    }
                )