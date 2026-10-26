
from pathlib import Path

from btime_rpa.domain.ports.exchange_rate_collector import (
    ExchangeRateCollector,
)
from btime_rpa.domain.ports.exchange_rate_exporter import (
    ExchangeRateExporter,
)


class CollectExchangeRates:
    """Caso de uso responsável por coletar e exportar cotações."""

    def __init__(
        self,
        collector: ExchangeRateCollector,
        exporter: ExchangeRateExporter,
    ) -> None:
        self._collector = collector
        self._exporter = exporter

    def execute(self, destination: Path) -> int:
        """Executa a coleta e exporta os resultados.

        Returns:
            Quantidade de cotações exportadas.
        """
        exchange_rates = self._collector.collect()

        if not exchange_rates:
            raise ValueError("Nenhuma cotação foi encontrada.")

        self._exporter.export(exchange_rates, destination)

        return len(exchange_rates)
