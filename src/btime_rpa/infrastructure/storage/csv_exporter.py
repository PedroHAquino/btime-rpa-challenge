
import csv
from pathlib import Path

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_exporter import (
    ExchangeRateExporter,
)


class CsvExchangeRateExporter(ExchangeRateExporter):
    """Exporta cotações para arquivos CSV padronizados."""

    FIELDNAMES = (
        "currency",
        "base_currency",
        "rate",
        "collected_at",
        "source",
    )

    def export(
        self,
        exchange_rates: list[ExchangeRate],
        destination: Path,
    ) -> None:
        """Grava as cotações em CSV, criando o diretório quando necessário.

        Args:
            exchange_rates: Cotações a gravar.
            destination: Caminho do arquivo CSV de saída.
        """
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

            for exchange_rate in exchange_rates:
                writer.writerow(
                    {
                        "currency": exchange_rate.currency,
                        "base_currency": exchange_rate.base_currency,
                        "rate": str(exchange_rate.rate),
                        "collected_at": (
                            exchange_rate.collected_at.isoformat()
                        ),
                        "source": exchange_rate.source,
                    }
                )
