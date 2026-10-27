from decimal import Decimal

import pytest

from btime_rpa.infrastructure.storage.csv_reader import CsvExchangeRateReader


def test_reads_valid_csv(tmp_path):
    """Verifica a leitura correta de duas cotações."""
    csv_file = tmp_path / "rates.csv"
    csv_file.write_text(
        "currency,base_currency,rate,collected_at,source\n"
        "USD,BRL,5.3441,2026-10-27T12:00:00+00:00,AwesomeAPI\n"
        "EUR,BRL,5.9555,2026-10-27T12:00:00+00:00,AwesomeAPI\n",
        encoding="utf-8",
    )

    rates = CsvExchangeRateReader().read(csv_file)

    assert len(rates) == 2
    assert rates[0].currency == "USD"
    assert rates[0].rate == Decimal("5.3441")
    assert rates[1].currency == "EUR"
    assert rates[1].rate == Decimal("5.9555")


def test_rejects_missing_file(tmp_path):
    """Verifica o tratamento de arquivos inexistentes."""
    csv_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        CsvExchangeRateReader().read(csv_file)


def test_rejects_invalid_header(tmp_path):
    """Verifica a validação das colunas obrigatórias."""
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(
        "currency,rate\nUSD,5.3441\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Cabeçalho CSV inválido"):
        CsvExchangeRateReader().read(csv_file)


def test_rejects_invalid_rate(tmp_path):
    """Verifica o tratamento de valores inválidos."""
    csv_file = tmp_path / "invalid_rate.csv"
    csv_file.write_text(
        "currency,base_currency,rate,collected_at,source\n"
        "USD,BRL,abc,2026-10-27T12:00:00+00:00,AwesomeAPI\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="linha 2"):
        CsvExchangeRateReader().read(csv_file)


def test_rejects_naive_datetime(tmp_path):
    """Verifica que datas sem fuso horário são rejeitadas."""
    csv_file = tmp_path / "invalid_date.csv"
    csv_file.write_text(
        "currency,base_currency,rate,collected_at,source\n"
        "USD,BRL,5.3441,2026-10-27T12:00:00,AwesomeAPI\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="linha 2"):
        CsvExchangeRateReader().read(csv_file)