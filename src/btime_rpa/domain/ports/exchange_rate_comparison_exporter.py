from abc import ABC, abstractmethod
from pathlib import Path

from btime_rpa.domain.entities.comparison_result import ComparisonResult


class ExchangeRateComparisonExporter(ABC):
    """Contrato para exportação de comparações de cotações."""

    @abstractmethod
    def export(
        self,
        result: ComparisonResult,
        destination: Path,
    ) -> None:
        """Exporta o resultado da comparação para o destino informado."""