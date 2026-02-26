"""HTML formatter for Telegram messages with length-aware splitting."""

import html
import json
import logging


__all__ = ("TelegramFormatter",)


class TelegramFormatter(logging.Formatter):
    """Format log records as HTML ``<code>`` blocks for the Telegram Bot API.

    Messages that fit within :attr:`MAX_MESSAGE_LEN` (4096 chars) are sent as
    regular messages.  Longer messages are split: a truncated caption
    (up to :attr:`MAX_CAPTION_LEN` chars) is sent alongside the full text
    as a document attachment.
    """

    parse_mode = "HTML"
    MAX_MESSAGE_LEN = 4096
    MAX_CAPTION_LEN = 1024

    def format_advanced(self, record):
        """Return a ``(caption, text)`` tuple for Telegram delivery.

        * If the message fits in a single Telegram message, *caption* is
          ``None`` and *text* contains the full HTML-wrapped content.
        * If the message is too long, *caption* is a truncated HTML preview
          and *text* is the raw full-length message (sent as a document).
        """
        msg = self.format(record)
        escaped = html.escape(msg)
        coded_escaped = f"<code>{escaped}</code>"

        if len(coded_escaped) < self.MAX_MESSAGE_LEN:
            return None, coded_escaped

        del coded_escaped
        return f"<code>{escaped[: self.MAX_CAPTION_LEN]}</code>", msg

    def format(self, record):
        """Format the record message, pretty-printing JSON if possible."""
        msg = record.getMessage()
        try:
            info = json.loads(msg)
            return json.dumps(info, indent=1, sort_keys=True, ensure_ascii=False, default=str)

        except Exception:
            return msg
