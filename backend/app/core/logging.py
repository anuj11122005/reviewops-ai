"""Structured JSON logging setup for the ReviewOps AI backend.

All log output is JSON-formatted for machine readability and structured
querying. Call ``setup_logging()`` once at application startup.
No module should use ``print()`` — use the ``logging`` module instead.
"""

import logging
import sys

from pythonjsonlogger.json import JsonFormatter


def setup_logging(*, level: int = logging.INFO) -> None:
    """Configure the root logger with a JSON formatter on stdout."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on repeated calls (e.g. tests).
    root.handlers.clear()
    root.addHandler(handler)

    # Quieten noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
