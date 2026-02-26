"""JSON formatter with rich exception context via structlog."""

import json
from logging import Formatter, LogRecord
from typing import ClassVar

from structlog import tracebacks

from .. import helper


class JsonFormatter(Formatter):
    """Serialize the full log record as a JSON string.

    Exception tracebacks are converted to structured dicts using
    :class:`structlog.tracebacks.ExceptionDictTransformer`, and stack-info
    frames are extracted via :func:`~thinlog.helper.parse_stack_info`.

    :param show_locals: If ``True``, local variables are included in
        exception tracebacks.
    """

    transformer: ClassVar[tracebacks.ExceptionDictTransformer]

    def __init__(self, show_locals: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.__class__.transformer = tracebacks.ExceptionDictTransformer(show_locals=show_locals)

    def format(self, record: LogRecord) -> str:
        """Return the record as a JSON string."""
        return json.dumps(self.format_record(record), default=str)

    def formatException(self, ei):
        """Format exception info as a JSON string, falling back to the standard formatter."""
        try:
            return json.dumps(self.format_exception(ei), default=str)

        except AttributeError:
            return super().formatException(ei)

    @classmethod
    def format_record(cls, record) -> dict:
        """Convert a :class:`~logging.LogRecord` to a plain dict.

        Handles ``exc_info`` (via structlog transformer) and ``stack_info``
        (via :func:`~thinlog.helper.parse_stack_info`).
        """
        d = {**record.__dict__}
        d.pop("handlers_context", None)

        if record.exc_info:
            try:
                if not record.exc_text:
                    raise ValueError

                d["tb"] = json.loads(record.exc_text)

            except Exception:
                d["tb"] = cls.format_exception(record.exc_info)
                record.exc_text = json.dumps(d["tb"], default=str)

        if record.stack_info and (not record.exc_info or d.get("force_extract_stack_info", False)):
            # We have no exc but a stack info requested
            d["frames"] = helper.parse_stack_info(record.stack_info)

        d.pop("exc_info", None)
        d.pop("stack_info", None)
        d.pop("exc_text", None)
        return d

    @classmethod
    def format_exception(cls, ei):
        """Transform exception info into a structured dict via structlog."""
        return cls.transformer(ei)
