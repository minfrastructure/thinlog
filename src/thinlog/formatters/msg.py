"""Minimal formatter that returns only the log message."""

import logging


__all__ = ("MsgFormatter",)


class MsgFormatter(logging.Formatter):
    """Return just the formatted message string, discarding all other record fields."""

    def format(self, record: logging.LogRecord) -> str:
        """Return :meth:`record.getMessage() <logging.LogRecord.getMessage>`."""
        return record.getMessage()
