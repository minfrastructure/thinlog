Formatters
==========

Thinlog provides three formatters covering structured output, plain text,
and Telegram-ready HTML.

JsonFormatter
-------------

:class:`~thinlog.formatters.JsonFormatter` serialises the entire
:class:`~logging.LogRecord` as a JSON string.  Exception tracebacks are
converted to structured dicts using
:class:`structlog.tracebacks.ExceptionDictTransformer`, giving you rich
exception context (frames, locals) in machine-readable form.

See :class:`~thinlog.formatters.JsonFormatter` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.formatters]
   json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = false}

Set ``show_locals = true`` to include local variables in exception tracebacks
(helpful for debugging, but be mindful of sensitive data).

**Stack info** — when ``stack_info=True`` is passed to the log call and there
is no exception, :class:`~thinlog.formatters.JsonFormatter` parses the stack
trace into structured frames via :func:`~thinlog.helper.parse_stack_info`.

MsgFormatter
------------

:class:`~thinlog.formatters.MsgFormatter` returns just the formatted message
string, discarding all other record fields.  Useful when you only need the
human-readable message (e.g., for console output alongside a structured
handler).

See :class:`~thinlog.formatters.MsgFormatter` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.formatters]
   msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}

TelegramFormatter
-----------------

:class:`~thinlog.formatters.TelegramFormatter` wraps the log message in
HTML ``<code>`` tags for the Telegram Bot API.  It handles length limits
automatically:

* Messages under 4096 characters → sent as a single ``<code>`` block.
* Longer messages → split into a truncated caption (up to 1024 chars) and
  the full raw text (sent as a document by :class:`~thinlog.handlers.TelegramHandler`).

If the message is valid JSON, it is pretty-printed before formatting.

See :class:`~thinlog.formatters.TelegramFormatter` in the :doc:`api`.

**TOML configuration:**

.. code-block:: toml

   [logging.formatters]
   telegram = {"()" = "thinlog.formatters.telegram.TelegramFormatter"}
