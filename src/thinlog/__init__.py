"""Thinlog -- a lightweight, fully-typed logging toolkit built on Python's standard :mod:`logging`.

Thinlog extends :mod:`logging` with advanced filtering, structured JSON formatting,
and remote log delivery (HTTP and Telegram) while staying thin and transparent.

Public API:

* :func:`configure_logging` -- set up logging from a :class:`LoggingSettings` or dict.
* :func:`get_logger` -- create a :class:`KeywordFriendlyLogger` and register it.
* :class:`KeywordFriendlyLogger` -- logger adapter that forwards keyword arguments as *extra* fields.
* :class:`LoggingSettings` -- typed dataclass matching :func:`logging.config.dictConfig` schema.
* :class:`RegisteredLoggers` -- global registry of logger names used by the wildcard feature.
"""

from .__version__ import __version__
from .bootstraping import configure_logging
from .log import KeywordFriendlyLogger
from .registered_loggers import RegisteredLoggers
from .settings import LoggingSettings
from .util import get_logger


__all__ = (
    "__version__",
    "configure_logging",
    "KeywordFriendlyLogger",
    "get_logger",
    "RegisteredLoggers",
    "LoggingSettings",
)
