
from abc import ABC, abstractmethod
from pathlib import Path

from btime_rpa.domain.entities.exchange_rate import ExchangeRate


class ExchangeRateExporter(ABC):
    """Contrato para exportação de cotações de moedas."""

    @abstractmethod
    def export(
        self,
        exchange_rates: list[ExchangeRate],
        destination: Path,
    ) -> None:
        """Exporta as cotações para o destino informado."""
