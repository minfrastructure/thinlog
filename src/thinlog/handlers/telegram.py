"""Handler that sends log records to Telegram via the Bot API."""

import logging
import warnings
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Self

import httpx

from ..formatters.telegram import TelegramFormatter


__all__ = ("TelegramHandler", "TelegramHandlerSettings")


@dataclass(unsafe_hash=True)
class TelegramHandlerSettings:
    """Settings for :class:`TelegramHandler`.

    The first instance created is stored as a global singleton accessible via
    :meth:`global_instance`.

    :param token: Telegram Bot API token.
    :param chat_id: Target chat ID (group, channel, or user).
    :param topic_id: Optional forum topic (message thread) ID.
    :param level: Minimum log level (name or int).
    :param timeout: HTTP request timeout in seconds.
    :param disable_notification: Send silently.
    :param disable_web_page_preview: Disable link previews in messages.
    :param proxy: Optional HTTP proxy URL.
    """

    token: str
    chat_id: int | str
    topic_id: int | str | None = None
    level: str | int = logging.NOTSET
    timeout: int = 5
    disable_notification: bool = False
    disable_web_page_preview: bool = True
    proxy: str | None = None

    __global_instance = None

    def __post_init__(self):
        if not self.__class__.__global_instance:
            self.__class__.__global_instance = self

    @classmethod
    def global_instance(cls) -> Optional[Self]:
        """Return the first-created settings instance, or ``None``."""
        return cls.__global_instance


class TelegramHandler(logging.Handler):
    """Send log records to a Telegram chat via the Bot API.

    Short messages are sent as regular Telegram messages.  Messages exceeding
    :attr:`~thinlog.formatters.TelegramFormatter.MAX_MESSAGE_LEN` are uploaded
    as document attachments with a truncated caption.

    Per-record overrides (chat_id, token, topic_id, disable) can be provided
    via a ``handlers_context.telegram`` dict on the log record.

    :param settings: A :class:`TelegramHandlerSettings` or a dict of its fields.
    """

    API_ENDPOINT = "https://api.telegram.org"

    def __init__(self, settings: TelegramHandlerSettings | dict):
        if isinstance(settings, dict):
            settings = TelegramHandlerSettings(**settings)

        self.settings = settings

        self._client = None

        self.token = self.settings.token
        self.disable_web_page_preview = self.settings.disable_web_page_preview
        self.disable_notification = self.settings.disable_notification
        self.timeout = self.settings.timeout
        self.chat_id = self.settings.chat_id
        self.topic_id = self.settings.topic_id

        super().__init__(level=self.settings.level)

    @property
    def client(self):
        """Lazily initialised :class:`httpx.Client`."""
        if not self._client:
            self._client = httpx.Client(
                timeout=self.settings.timeout, base_url=self.API_ENDPOINT, proxy=self.settings.proxy
            )

        return self._client

    @classmethod
    def format_url(cls, token, method):
        """Build a Telegram Bot API URL for the given *method*."""
        return "%s/bot%s/%s" % (cls.API_ENDPOINT, token, method)

    def request(self, method, bot_token: Optional[str] = None, **kwargs):
        """Call a Telegram Bot API *method* and return the JSON response."""
        url = self.format_url(bot_token or self.token, method)

        response = self.client.post(url, **kwargs)
        return response.json()

    def send_message(self, text, **kwargs):
        """Send a text message via ``sendMessage``."""
        data = {"text": text}
        data.update(kwargs)
        return self.request("sendMessage", json=data)

    def send_document(self, text, document, **kwargs):
        """Send a document with a caption via ``sendDocument``."""
        data = {"caption": text}
        data.update(kwargs)
        return self.request("sendDocument", data=data, files={"document": ("details.json", document, "text/plain")})

    def close(self):
        """Close the underlying HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

    def emit(self, record):
        """Format the record and send it to Telegram.

        Short messages are sent via ``sendMessage``; long messages are
        uploaded as a document via ``sendDocument``.  Supports per-record
        overrides via ``record.handlers_context["telegram"]``.
        """
        tg_ctx = record.__dict__.get("handlers_context", dict()).get("telegram", dict())
        if tg_ctx.get("disable"):
            return

        if hasattr(self.formatter, "format_advanced"):
            caption, text = self.formatter.format_advanced(record)

        else:
            text = self.format(record)
            caption = (
                None if len(text) < TelegramFormatter.MAX_MESSAGE_LEN else text[: TelegramFormatter.MAX_CAPTION_LEN]
            )

        if not text:
            return

        data = {
            "chat_id": tg_ctx.get("chat_id", self.chat_id),
            "disable_web_page_preview": tg_ctx.get("disable_web_page_preview", self.disable_web_page_preview),
            "disable_notification": tg_ctx.get("disable_notification", self.disable_notification),
        }

        if tg_ctx.get("topic_id", self.topic_id):
            data["message_thread_id"] = tg_ctx.get("topic_id", self.topic_id)

        if hasattr(self.formatter, "parse_mode"):
            data["parse_mode"] = self.formatter.parse_mode

        if tg_ctx.get("token", None):
            data["bot_token"] = tg_ctx["token"]

        try:
            if caption is None:
                response = self.send_message(text, **data)
            else:
                response = self.send_document(caption, document=BytesIO(text.encode()), **data)

        except Exception:
            self.handleError(record)
            return

        if response and not response.get("ok", False):
            warnings.warn("Telegram responded with ok=false status! {}".format(response))
