"""Bootstrap logging configuration via :func:`logging.config.dictConfig`."""

import atexit
import logging.config
import logging.handlers
from collections.abc import Iterator
from dataclasses import asdict
from typing import Any

from .log import KeywordFriendlyLogger
from .registered_loggers import RegisteredLoggers
from .settings import LoggingSettings
from .util import get_logger


def configure_logging(
    name: str,
    config: LoggingSettings | dict[str, Any],
    extra: dict[str, Any] | None = None,
    more_loggers: list[str] | None = None,
    include_default_logger: bool = False,
    include_registered_loggers: bool = False,
    include_root_logger: bool = False,
    disable_log_errors: bool = True,
) -> KeywordFriendlyLogger:
    """Set up the logging system and return a ready-to-use logger.

    Applies the configuration, starts any
    :class:`~logging.handlers.QueueHandler` listener, and registers an
    :func:`atexit` handler that stops the listener and calls
    :func:`logging.shutdown` on interpreter exit.

    **Wildcard loggers:** If the *config* contains a logger named ``"*"``, its
    settings are copied to every logger listed in *more_loggers* (and those
    gathered from :class:`RegisteredLoggers`).  A specific logger can set
    ``"merge": true`` to extend rather than replace the wildcard config.

    :param name: Name of the primary logger to return.
    :param config: A :class:`LoggingSettings` instance or a raw dict suitable
        for :func:`logging.config.dictConfig`.
    :param extra: Default *extra* fields for the returned logger.
    :param more_loggers: Additional logger names to configure via the wildcard.
    :param include_default_logger: If ``True``, add *name* to *more_loggers*.
    :param include_registered_loggers: If ``True``, include all names from
        :class:`RegisteredLoggers`.
    :param include_root_logger: If ``True``, apply the wildcard config to the
        root logger as well.
    :param disable_log_errors: If ``True`` (default), set
        :data:`logging.raiseExceptions` to ``False``.
    :returns: A :class:`KeywordFriendlyLogger` instance.
    """
    if disable_log_errors:
        logging.raiseExceptions = False

    if not more_loggers:
        more_loggers = []

    if include_default_logger:
        more_loggers.append(name)

    if include_registered_loggers:
        more_loggers.extend(RegisteredLoggers.get_registered_logger_names())

    more_loggers = list(set(more_loggers))

    def _iter_loggers() -> Iterator[logging.Logger]:
        nonlocal more_loggers

        for _lh in more_loggers:
            yield logging.getLogger(_lh)

    if not isinstance(config, dict):
        config = asdict(config)

    config.setdefault("loggers", dict())
    config.setdefault("root", dict())

    wildcard_logger = config["loggers"].pop("*", None)
    if wildcard_logger:
        for founded_logger in _iter_loggers():
            if founded_logger.name in config["loggers"]:
                _allow_merge = config["loggers"][founded_logger.name].pop("merge", False)
                if _allow_merge:
                    tmp = {**wildcard_logger}
                    for _k, _v in config["loggers"][founded_logger.name].items():
                        if _k not in tmp:
                            tmp[_k] = _v
                            continue

                        if isinstance(tmp[_k], dict):
                            tmp[_k].update(_v)

                        elif isinstance(tmp[_k], list):
                            tmp[_k].extend(_v)

                        else:
                            tmp[_k] = _v

                    config["loggers"][founded_logger.name] = tmp

                continue

            config["loggers"][founded_logger.name] = {**wildcard_logger}

        if include_root_logger and not config["root"]:
            config["root"] = {**wildcard_logger}
            config["root"].pop("propagate", None)

    if not config["root"]:
        config.pop("root", None)

    logging.config.dictConfig(config)

    listener = None
    for _handler_name in logging.getHandlerNames():
        _handler = logging.getHandlerByName(_handler_name)
        if isinstance(_handler, logging.handlers.QueueHandler):
            listener = _handler.listener
            break

    if listener:
        listener.start()

    def _shutdown_handler() -> None:
        if listener:
            listener.stop()

        logging.shutdown()

    atexit.register(_shutdown_handler)
    return get_logger(name, extra)
