import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from btime_rpa.domain.entities.exchange_rate import ExchangeRate
from btime_rpa.domain.ports.exchange_rate_reader import ExchangeRateReader


class CsvExchangeRateReader(ExchangeRateReader):
    """Lê cotações de arquivos CSV."""

    FIELDNAMES = {
        "currency",
        "base_currency",
        "rate",
        "collected_at",
        "source",
    }

    def read(self, source: Path) -> list[ExchangeRate]:
        """Lê e valida as cotações de um arquivo CSV."""
        if not source.is_file():
            raise FileNotFoundError(
                f"Arquivo de cotações não encontrado: {source}"
            )

        exchange_rates = []

        with source.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or not self.FIELDNAMES.issubset(
                reader.fieldnames
            ):
                raise ValueError(
                    f"Cabeçalho CSV inválido: {source}"
                )

            for line_number, row in enumerate(reader, start=2):
                try:
                    exchange_rate = ExchangeRate(
                        currency=row["currency"],
                        base_currency=row["base_currency"],
                        rate=Decimal(row["rate"]),
                        collected_at=datetime.fromisoformat(
                            row["collected_at"]
                        ),
                        source=row["source"],
                    )
                except (
                    ValueError,
                    TypeError,
                    InvalidOperation,
                    KeyError,
                ) as exc:
                    raise ValueError(
                        f"Cotação inválida na linha {line_number} "
                        f"do arquivo {source}"
                    ) from exc

                exchange_rates.append(exchange_rate)

        return exchange_rates