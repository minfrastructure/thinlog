"""Handler that prints a record's ``context`` attribute as JSON to stdout."""

import json
import logging


class CtxPrintHandler(logging.Handler):
    """Print the ``context`` attribute of a log record as JSON to stdout.

    If the record has no ``context`` attribute the handler silently does nothing.
    Useful for debugging context filters during development.
    """

    def emit(self, record):
        """Print ``record.context`` as a JSON string."""
        try:
            print(json.dumps(record.context, default=str))  # type: ignore

        except AttributeError:
            pass
