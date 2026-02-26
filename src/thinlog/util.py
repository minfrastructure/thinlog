"""Factory for creating and registering loggers."""

import logging
from typing import Any

from .log import KeywordFriendlyLogger
from .registered_loggers import RegisteredLoggers


def get_logger(name: str, extra: dict[str, Any] | None, register: bool = True) -> KeywordFriendlyLogger:
    """Create a :class:`KeywordFriendlyLogger` and optionally register it.

    :param name: Logger name (passed to :func:`logging.getLogger`).
    :param extra: Default *extra* fields attached to every record.
    :param register: If ``True`` (default), add *name* to
        :class:`RegisteredLoggers` so it is picked up by the wildcard
        feature in :func:`configure_logging`.
    :returns: A :class:`~logging.LoggerAdapter` wrapping the named logger.
    """
    if register:
        RegisteredLoggers.loggers.add(name)

    return KeywordFriendlyLogger(logging.getLogger(name), extra)
