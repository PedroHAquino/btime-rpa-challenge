"""Executa a comparação entre cotações da API e do scraping."""

import logging
from pathlib import Path

from btime_rpa.application.use_cases.compare_exchange_rates import (
    CompareExchangeRates,
)
from btime_rpa.infrastructure.storage.csv_comparison_exporter import (
    CsvExchangeRateComparisonExporter,
)
from btime_rpa.infrastructure.storage.csv_reader import (
    CsvExchangeRateReader,
)

LOGGER = logging.getLogger(__name__)


def main() -> int:
    """Compara as cotações e retorna o código de saída."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    api_source = Path("data/api_exchange_rates.csv")
    scraping_source = Path("data/scraping_exchange_rates.csv")
    destination = Path("data/comparison_exchange_rates.csv")

    use_case = CompareExchangeRates(
        reader=CsvExchangeRateReader(),
    )

    exporter = CsvExchangeRateComparisonExporter()

    try:
        LOGGER.info("Iniciando comparação de cotações")

        result = use_case.execute(
            api_source=api_source,
            scraping_source=scraping_source,
        )

        exporter.export(result, destination)

    except (RuntimeError, ValueError, OSError) as exc:
        LOGGER.error("Falha na comparação: %s", exc)
        return 1

    LOGGER.info(
        "%s pares de moedas comparados",
        len(result.comparisons),
    )
    LOGGER.info(
        "%s pares ausentes na API",
        len(result.missing_in_api),
    )
    LOGGER.info(
        "%s pares ausentes no scraping",
        len(result.missing_in_scraping),
    )
    LOGGER.info("Arquivo gerado: %s", destination)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())