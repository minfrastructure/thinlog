"""Typed dataclass matching the :func:`logging.config.dictConfig` schema."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LoggingSettings:
    """Configuration container for :func:`logging.config.dictConfig`.

    All fields mirror the keys accepted by :func:`logging.config.dictConfig`.
    Convert to a plain dict with :func:`dataclasses.asdict` before passing to
    ``dictConfig`` (this is handled automatically by :func:`configure_logging`).

    :param version: Schema version -- must be ``1``.
    :param formatters: Formatter definitions keyed by name.
    :param filters: Filter definitions keyed by name.
    :param handlers: Handler definitions keyed by name.
    :param loggers: Logger definitions keyed by name.
    :param incremental: If ``True``, merge into the existing configuration.
    :param disable_existing_loggers: If ``True``, disable loggers not in *loggers*.
    :param root: Configuration for the root logger.
    """
    version: int = field(default=1)
    formatters: dict[str, dict[str, Any]] = field(default_factory=dict)
    filters: dict[str, dict[str, Any]] = field(default_factory=dict)
    handlers: dict[str, dict[str, Any]] = field(default_factory=dict)
    loggers: dict[str, dict[str, Any]] = field(default_factory=dict)
    incremental: bool = field(default=False)
    disable_existing_loggers: bool = field(default=False)
    root: dict[str, Any] = field(default_factory=dict)
