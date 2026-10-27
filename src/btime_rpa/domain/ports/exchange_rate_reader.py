from abc import ABC, abstractmethod
from pathlib import Path

from btime_rpa.domain.entities.exchange_rate import ExchangeRate


class ExchangeRateReader(ABC):
    """Contrato para leitura de cotações de uma fonte persistida."""

    @abstractmethod
    def read(self, source: Path) -> list[ExchangeRate]:
        """Lê cotações e retorna entidades de domínio."""
