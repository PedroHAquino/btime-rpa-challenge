
from abc import ABC, abstractmethod

from btime_rpa.domain.entities.exchange_rate import ExchangeRate


class ExchangeRateCollector(ABC):
    """Contrato para coletores de cotações de moedas."""

    @abstractmethod
    def collect(self) -> list[ExchangeRate]:
        """Coleta e retorna cotações normalizadas.

        Returns:
            Cotações coletadas no formato de domínio.
        """
