from pathlib import Path
from unittest.mock import Mock

import pytest

from btime_rpa import run_comparison


def test_main_returns_zero_on_success(monkeypatch):
    """Retorna zero quando a comparação é concluída com sucesso."""
    result = Mock(
        comparisons=[Mock(), Mock()],
        missing_in_api=[],
        missing_in_scraping=[],
    )

    execute = Mock(return_value=result)
    export = Mock()

    monkeypatch.setattr(
        run_comparison,
        "CompareExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )
    monkeypatch.setattr(
        run_comparison,
        "CsvExchangeRateComparisonExporter",
        Mock(return_value=Mock(export=export)),
    )

    exit_code = run_comparison.main()

    assert exit_code == 0

    execute.assert_called_once_with(
        api_source=Path("data/api_exchange_rates.csv"),
        scraping_source=Path("data/scraping_exchange_rates.csv"),
    )

    export.assert_called_once_with(
        result,
        Path("data/comparison_exchange_rates.csv"),
    )


@pytest.mark.parametrize(
    "exception",
    [
        RuntimeError("Falha na comparação"),
        ValueError("Cotação inválida"),
        OSError("Erro ao acessar CSV"),
    ],
)
def test_main_returns_one_on_comparison_error(
    monkeypatch,
    exception,
):
    """Retorna um quando a comparação falha."""
    execute = Mock(side_effect=exception)
    export = Mock()

    monkeypatch.setattr(
        run_comparison,
        "CompareExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )
    monkeypatch.setattr(
        run_comparison,
        "CsvExchangeRateComparisonExporter",
        Mock(return_value=Mock(export=export)),
    )

    assert run_comparison.main() == 1
    export.assert_not_called()


def test_main_returns_one_on_export_error(monkeypatch):
    """Retorna um quando a exportação do relatório falha."""
    result = Mock(
        comparisons=[],
        missing_in_api=[],
        missing_in_scraping=[],
    )

    execute = Mock(return_value=result)
    export = Mock(side_effect=OSError("Falha ao gravar relatório"))

    monkeypatch.setattr(
        run_comparison,
        "CompareExchangeRates",
        Mock(return_value=Mock(execute=execute)),
    )
    monkeypatch.setattr(
        run_comparison,
        "CsvExchangeRateComparisonExporter",
        Mock(return_value=Mock(export=export)),
    )

    assert run_comparison.main() == 1
    export.assert_called_once_with(
        result,
        Path("data/comparison_exchange_rates.csv"),
    )