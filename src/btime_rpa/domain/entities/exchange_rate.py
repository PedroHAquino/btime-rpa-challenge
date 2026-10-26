
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ExchangeRate:
    currency: str
    base_currency: str
    rate: Decimal
    collected_at: datetime
    source: str

    def __post_init__(self) -> None:
        if not self.currency or not self.base_currency:
            raise ValueError("Os códigos das moedas são obrigatórios.")

        if self.currency == self.base_currency:
            raise ValueError("As moedas devem ser diferentes.")

        if not self.rate.is_finite() or self.rate <= 0:
            raise ValueError("A cotação deve ser positiva e finita.")

        if self.collected_at.tzinfo is None:
            raise ValueError("A data da coleta deve conter fuso horário.")

        if not self.source:
            raise ValueError("A origem da cotação é obrigatória.")
