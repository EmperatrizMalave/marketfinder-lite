"""Logging sin secretos."""

from __future__ import annotations

import logging

from marketfinder.utils.logging import RedactFilter, setup_logging


def test_logging_redacts_secrets(data_dir, caplog) -> None:
    logger = setup_logging(data_dir=data_dir, force=True)
    # Verificar filtro
    record = logging.LogRecord(
        name="marketfinder",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="got access_token=supersecret and client_secret=abc",
        args=(),
        exc_info=None,
    )
    filt = RedactFilter()
    assert filt.filter(record) is True
    assert "supersecret" not in record.getMessage() or "***REDACTED***" in str(record.msg)

    logger.info("refresh_token=should_hide")
    log_file = data_dir / "logs" / "marketfinder.log"
    assert log_file.is_file()
    content = log_file.read_text(encoding="utf-8")
    assert "Logging iniciado" in content
