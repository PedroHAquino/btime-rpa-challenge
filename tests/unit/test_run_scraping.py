from pathlib import Path
from unittest.mock import Mock

import pytest

from btime_rpa import run_scraping


def test_main_returns_zero_on_success(monkeypatch):
    """Retorna zero quando o scraping termina com sucesso."""

    execute = Mock(return_value=2)

    monkeypatch.setattr(
        run_scraping,
        "CollectExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )

    result = run_scraping.main()

    assert result == 0
    execute.assert_called_once_with(
        Path("data/scraping_exchange_rates.csv")
    )


@pytest.mark.parametrize(
    "exception",
    [
        RuntimeError("Google Finance indisponível"),
        ValueError("Cotação não encontrada"),
        OSError("Erro ao gravar CSV"),
    ],
)
def test_main_returns_one_on_error(monkeypatch, exception):
    """Retorna um quando ocorre uma falha no scraping."""

    execute = Mock(side_effect=exception)

    monkeypatch.setattr(
        run_scraping,
        "CollectExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )

    result = run_scraping.main()

    assert result == 1
