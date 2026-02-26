"""Bootstrap logging configuration via :func:`logging.config.dictConfig`."""

import logging.config
import logging.handlers
from dataclasses import asdict
from typing import Generator

from .log import KeywordFriendlyLogger
from .registered_loggers import RegisteredLoggers
from .settings import LoggingSettings
from .util import get_logger


def configure_logging(
    name: str,
    config: LoggingSettings | dict,
    extra: dict = None,
    more_loggers: list = None,
    include_default_logger: bool = False,
    include_registered_loggers: bool = False,
    include_root_logger: bool = False,
    disable_log_errors: bool = True,
) -> Generator[KeywordFriendlyLogger]:
    """Set up the logging system and yield a ready-to-use logger.

    This is a **generator function** -- use it with a ``with`` statement or
    call ``next()`` / iterate over it.  On entry it applies the configuration
    and starts any :class:`~logging.handlers.QueueHandler` listener; on exit
    it stops the listener and calls :func:`logging.shutdown`.

    **Wildcard loggers:** If the *config* contains a logger named ``"*"``, its
    settings are copied to every logger listed in *more_loggers* (and those
    gathered from :class:`RegisteredLoggers`).  A specific logger can set
    ``"merge": true`` to extend rather than replace the wildcard config.

    :param name: Name of the primary logger to yield.
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
    :returns: A generator yielding a single :class:`KeywordFriendlyLogger`.
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

    def _iter_loggers():
        nonlocal more_loggers

        for _lh in more_loggers:
            yield logging.getLogger(_lh)

    if not isinstance(config, dict):
        config = asdict(config)  # type: ignore[type]

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
            listener = _handler.listener  # type: ignore
            break

    if listener:
        listener.start()

    yield get_logger(name, extra)  # type: ignore

    if listener:
        listener.stop()

    logging.shutdown()
