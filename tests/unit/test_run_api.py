from pathlib import Path
from unittest.mock import Mock

import pytest

from btime_rpa import run_api


def test_main_returns_zero_on_success(monkeypatch):
    """Retorna zero quando a coleta é concluída com sucesso."""

    execute = Mock(return_value=2)

    monkeypatch.setattr(
        run_api,
        "CollectExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )

    result = run_api.main()

    assert result == 0
    execute.assert_called_once_with(
        Path("data/api_exchange_rates.csv")
    )


@pytest.mark.parametrize(
    "exception",
    [
        RuntimeError("API indisponível"),
        ValueError("Cotação inválida"),
        OSError("Erro ao gravar CSV"),
    ],
)
def test_main_returns_one_on_error(monkeypatch, exception):
    """Retorna um quando ocorre uma falha na execução."""

    execute = Mock(side_effect=exception)

    monkeypatch.setattr(
        run_api,
        "CollectExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )

    result = run_api.main()

    assert result == 1