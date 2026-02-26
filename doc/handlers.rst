Handlers
========

Thinlog provides three handlers for delivering logs beyond the console.

JsonHTTPHandler
---------------

:class:`~thinlog.handlers.JsonHTTPHandler` sends formatted log records as
JSON via HTTP POST using `httpx <https://www.python-httpx.org/>`_.

See :class:`~thinlog.handlers.json_http.JsonHttpHandlerSettings` and
:class:`~thinlog.handlers.JsonHTTPHandler` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.handlers.http]
   "()" = "thinlog.handlers.json_http.JsonHTTPHandler"
   level = "WARNING"
   formatter = "json"
   settings = {url = "https://example.com/logs", headers = {token = "USERNAME:PASSWORD", cat = "myapp"}, timeout = 5}

**Per-record overrides** — use ``handlers_context.json_http`` on the record
(typically set by an :class:`~thinlog.filters.AssignerFilter`):

.. code-block:: python

   logger.warning(
       "Payment failed",
       handlers_context={"json_http": {"append_headers": {"cat": "billing"}}},
   )

Available override keys:

* ``disable`` -- skip this record.
* ``url`` -- override the target URL.
* ``headers`` -- replace default headers.
* ``append_headers`` -- merge additional headers into the defaults.

**Grouping by category** — the ``cat`` header is a common pattern for
routing logs on the server side.  Use the
:class:`~thinlog.filters.AssignerFilter` to assign different ``cat`` values
per logger:

.. code-block:: toml

   [logging.filters.assign_auth]
   "()" = "thinlog.filters.assigner.AssignerFilter"
   by_name = ["auth"]
   assignments = {handlers_context = {json_http = {append_headers = {cat = "auth"}}}}

TelegramHandler
---------------

:class:`~thinlog.handlers.TelegramHandler` sends logs to a Telegram chat
via the `Bot API <https://core.telegram.org/bots/api>`_.

See :class:`~thinlog.handlers.telegram.TelegramHandlerSettings` and
:class:`~thinlog.handlers.TelegramHandler` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.handlers.telegram]
   "()" = "thinlog.handlers.telegram.TelegramHandler"
   level = "WARNING"
   formatter = "telegram"
   settings = {token = "123456:ABC-DEF", chat_id = "-100123456789", topic_id = 12345}

**Message vs. document mode** — short messages (under 4096 characters) are
sent as regular Telegram messages.  Longer messages are automatically uploaded
as a ``details.json`` document with a truncated caption (up to 1024 characters).

**Forum topics** — set ``topic_id`` to send messages to a specific topic
(message thread) in a Telegram group with forum mode enabled.

**Per-record overrides** via ``handlers_context.telegram``:

* ``disable`` -- skip this record.
* ``chat_id`` -- send to a different chat.
* ``token`` -- use a different bot token.
* ``topic_id`` -- send to a different topic.
* ``disable_notification`` -- send silently.
* ``disable_web_page_preview`` -- suppress link previews.

CtxPrintHandler
---------------

:class:`~thinlog.handlers.CtxPrintHandler` prints the ``context`` attribute
of a log record as JSON to stdout.  This is useful during development to
inspect context data added by custom context filters.

See :class:`~thinlog.handlers.CtxPrintHandler` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.handlers]
   ctx = {"()" = "thinlog.handlers.ctx_print.CtxPrintHandler", level = "DEBUG"}

If the record has no ``context`` attribute (e.g., no context filters are
active), the handler silently does nothing.
