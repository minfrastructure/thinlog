"""Handler that sends JSON log records via HTTP POST."""

import json
import logging
from dataclasses import dataclass
from typing import Any, ClassVar

import httpx


__all__ = ("JsonHTTPHandler", "JsonHttpHandlerSettings")


MAX_MESSAGE_LEN = 4096


@dataclass(unsafe_hash=True)
class JsonHttpHandlerSettings:
    """Settings for :class:`JsonHTTPHandler`.

    The first instance created is stored as a global singleton accessible via
    :meth:`global_instance`.

    :param url: Target URL for HTTP POST requests.
    :param headers: Default HTTP headers sent with every request.
    :param level: Minimum log level (name or int).
    :param timeout: HTTP request timeout in seconds.
    :param proxy: Optional HTTP proxy URL.
    """

    url: str
    headers: dict[str, str]
    level: str | int = logging.NOTSET
    timeout: int = 5
    proxy: str | None = None

    __global_instance: ClassVar["JsonHttpHandlerSettings | None"] = None

    def __post_init__(self) -> None:
        if not self.__class__.__global_instance:
            self.__class__.__global_instance = self

    @classmethod
    def global_instance(cls) -> "JsonHttpHandlerSettings | None":
        """Return the first-created settings instance, or ``None``."""
        return cls.__global_instance


class JsonHTTPHandler(logging.Handler):
    """Send formatted log records as JSON via HTTP POST using :mod:`httpx`.

    The HTTP client is lazily initialised on first use.  Per-record overrides
    (URL, headers, disable) can be provided via a ``handlers_context.json_http``
    dict on the log record.

    :param settings: A :class:`JsonHttpHandlerSettings` or a dict of its fields.
    """

    def __init__(self, settings: JsonHttpHandlerSettings | dict[str, Any]) -> None:
        if isinstance(settings, dict):
            settings = JsonHttpHandlerSettings(**settings)

        self.settings = settings

        self._client: httpx.Client | None = None

        self.url = self.settings.url
        self.headers = self.settings.headers
        self.timeout = self.settings.timeout

        super().__init__(level=self.settings.level)

    @property
    def client(self) -> httpx.Client:
        """Lazily initialised :class:`httpx.Client`."""
        if not self._client:
            self._client = httpx.Client(timeout=self.settings.timeout, proxy=self.settings.proxy)

        return self._client

    def request(self, url: str, **kwargs: Any) -> Any:
        """Send an HTTP POST and return the parsed JSON response."""
        response = self.client.post(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def json_request(self, url: str, data: str | dict[str, Any], **kwargs: Any) -> Any:
        """POST *data* as JSON (parsing it first if it is a string)."""
        if isinstance(data, str):
            data = json.loads(data)

        kwargs["json"] = data
        return self.request(url, **kwargs)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def emit(self, record: logging.LogRecord) -> None:
        """Format and POST the record as JSON.

        Supports per-record overrides via ``record.handlers_context["json_http"]``:

        * ``disable`` -- skip this record entirely.
        * ``url`` -- override the target URL.
        * ``headers`` -- replace the default headers.
        * ``append_headers`` -- merge additional headers.
        """
        jh_ctx = record.__dict__.get("handlers_context", dict()).get("json_http", dict())
        if jh_ctx.get("disable"):
            return

        text = self.format(record)

        url = jh_ctx.get("url", self.url)
        headers = jh_ctx.get("headers", self.headers)
        headers.update(jh_ctx.get("append_headers", {}))

        try:
            self.json_request(url, text, headers=headers)

        except Exception:
            self.handleError(record)
            return
