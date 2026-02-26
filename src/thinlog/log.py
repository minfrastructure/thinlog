"""Logger adapter that converts keyword arguments into *extra* fields."""

import logging
from collections.abc import MutableMapping
from typing import Any


class KeywordFriendlyLogger(logging.LoggerAdapter[logging.Logger]):
    """A :class:`logging.LoggerAdapter` that passes arbitrary keyword arguments as *extra* fields.

    Standard :mod:`logging` requires extra data to be wrapped in an ``extra``
    dict.  :class:`KeywordFriendlyLogger` lets callers pass keyword arguments
    directly -- they are automatically moved into *extra* so that filters,
    formatters, and handlers can access them as record attributes.

    :param logger: The underlying :class:`logging.Logger` to adapt.
    :param extra: Optional default extra fields attached to every record.
    """

    ignored_meta_keys = ("exc_info", "stack_info", "stacklevel")

    def __init__(self, logger: logging.Logger, extra: dict[str, Any] | None = None) -> None:
        super().__init__(logger, extra or {})

    def process(self, msg: Any, metadata: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        """Move keyword arguments into the *extra* dict.

        Keys listed in :attr:`ignored_meta_keys` are left in *metadata* so
        that the standard logging machinery can handle them.

        :param msg: The log message.
        :param metadata: Keyword arguments passed to the logging call.
        :returns: A ``(msg, metadata)`` tuple ready for the underlying logger.
        """
        extra = metadata.pop("extra", {})
        extra.update(self.extra)

        for key, value in list(metadata.items()):
            if key not in self.ignored_meta_keys:
                extra[key] = metadata.pop(key)

        extra["stacklevel"] = metadata.get("stacklevel", 1)
        metadata["extra"] = extra
        return msg, metadata
