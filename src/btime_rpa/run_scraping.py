"""Executa a coleta de cotações via scraping do Google Finance."""

import logging
from pathlib import Path

from btime_rpa.application.use_cases.collect_exchange_rates import (
    CollectExchangeRates,
)
from btime_rpa.infrastructure.scraping.google_finance_collector import (
    GoogleFinanceCollector,
)
from btime_rpa.infrastructure.storage.csv_exporter import (
    CsvExchangeRateExporter,
)

LOGGER = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    destination = Path("data/scraping_exchange_rates.csv")

    use_case = CollectExchangeRates(
        collector=GoogleFinanceCollector(),
        exporter=CsvExchangeRateExporter(),
    )

    try:
        LOGGER.info("Iniciando coleta via Google Finance")
        total = use_case.execute(destination)
    except (RuntimeError, ValueError, OSError) as exc:
        LOGGER.error("Falha na coleta: %s", exc)
        return 1

    LOGGER.info("%s cotações exportadas", total)
    LOGGER.info("Arquivo gerado: %s", destination)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
