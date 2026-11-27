"""Logging estructurado a archivo (sin secretos)."""

from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

from marketfinder.utils.paths import logs_dir

_SECRET_PATTERN = re.compile(
    r"(client_secret|access_token|refresh_token|password|api_key|authorization)\s*[:=]\s*\S+",
    re.IGNORECASE,
)

_configured = False


class RedactFilter(logging.Filter):
    """Oculta valores que parecen secretos en mensajes de log."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        if _SECRET_PATTERN.search(msg):
            record.msg = _SECRET_PATTERN.sub(
                lambda m: f"{m.group(1)}=***REDACTED***", msg
            )
            record.args = ()
        return True


def setup_logging(
    *,
    data_dir: Path | str | None = None,
    level: int = logging.INFO,
    force: bool = False,
) -> logging.Logger:
    """Configura logger raíz de la app una sola vez."""
    global _configured
    logger = logging.getLogger("marketfinder")
    if _configured and not force:
        return logger

    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False

    log_path = logs_dir(data_dir) / "marketfinder.log"
    handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    handler.addFilter(RedactFilter())
    logger.addHandler(handler)

    # Consola silenciosa por defecto; útil en desarrollo
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
    console.addFilter(RedactFilter())
    logger.addHandler(console)

    _configured = True
    logger.info("Logging iniciado → %s", log_path)
    return logger


def get_logger(name: str = "marketfinder") -> logging.Logger:
    return logging.getLogger(name)
