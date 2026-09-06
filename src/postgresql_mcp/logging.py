"""Structured logging for DB Bridge — stderr only.

stdio MCP uses stdout for JSON-RPC. Any log line on stdout will break
clients. All structured logs must go to stderr.
"""

from __future__ import annotations

import logging
import sys
from typing import TextIO, cast

import structlog
from structlog.stdlib import BoundLogger


def configure_logging(level: str = "INFO", stream: TextIO | None = None) -> None:
    """Configure stdlib + structlog to write JSON lines to stderr."""
    log_stream = stream if stream is not None else sys.stderr
    log_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    logging.basicConfig(
        format="%(message)s",
        stream=log_stream,
        level=log_level,
        force=True,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )


def get_logger(name: str) -> BoundLogger:
    """Return a bound structlog logger."""
    return cast(BoundLogger, structlog.get_logger(name))
