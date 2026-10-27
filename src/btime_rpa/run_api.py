"""Executa a coleta de cotações pela AwesomeAPI."""

import logging
from pathlib import Path

from btime_rpa.application.use_cases.collect_exchange_rates import (
    CollectExchangeRates,
)
from btime_rpa.infrastructure.api.awesome_api_collector import (
    AwesomeApiCollector,
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

    destination = Path("data/api_exchange_rates.csv")

    use_case = CollectExchangeRates(
        collector=AwesomeApiCollector(),
        exporter=CsvExchangeRateExporter(),
    )

    try:
        LOGGER.info("Iniciando coleta via AwesomeAPI")
        total = use_case.execute(destination)
    except (RuntimeError, ValueError, OSError) as exc:
        LOGGER.error("Falha na coleta: %s", exc)
        return 1

    LOGGER.info("%s cotações exportadas", total)
    LOGGER.info("Arquivo gerado: %s", destination)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())