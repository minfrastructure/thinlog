"""Global registry of logger names for the wildcard configuration feature."""

from typing import ClassVar


class RegisteredLoggers:
    """Stores logger names so :func:`configure_logging` can apply wildcard configs to them.

    Loggers are registered automatically when created via :func:`get_logger`.
    """

    loggers: ClassVar[set[str]] = set()

    @classmethod
    def get_registered_logger_names(cls) -> list[str]:
        return list(cls.loggers)
