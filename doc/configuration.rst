Configuration
=============

Thinlog builds on Python's :func:`logging.config.dictConfig`.  You write your
logging configuration as a TOML file (or a dict) and pass it to
:func:`~thinlog.configure_logging`, which applies the config, manages
:class:`~logging.handlers.QueueHandler` listeners, and yields a ready-to-use
logger.

LoggingSettings
---------------

:class:`~thinlog.LoggingSettings` is a typed dataclass whose fields mirror the
keys accepted by :func:`logging.config.dictConfig`:

See :class:`~thinlog.LoggingSettings` in the :doc:`api`.

You can pass either a :class:`~thinlog.LoggingSettings` instance or a plain
dict to :func:`~thinlog.configure_logging` — the dict is used directly while
the dataclass is converted via :func:`dataclasses.asdict`.

TOML configuration structure
-----------------------------

Thinlog expects a ``[logging]`` table in your TOML config:

.. code-block:: toml

   [logging]
   root = {level = "INFO", handlers = ["queue"]}

   [logging.formatters]
   json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = false}
   msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "INFO", stream = "ext://sys.stderr", formatter = "msg"}
   queue = {class = "logging.handlers.QueueHandler", handlers = ["stream"], formatter = "json", respect_handler_level = true}

Load and apply it:

.. code-block:: python

   import tomllib
   from pathlib import Path
   from thinlog import configure_logging

   config = tomllib.loads(Path("config.toml").read_text())
   log_gen = configure_logging("myapp", config["logging"])
   logger = next(log_gen)

Wildcard logger (``"*"``)
--------------------------

When your application has many loggers (one per module, one per library, etc.),
configuring each one individually is tedious.  Thinlog's **wildcard logger**
solves this:

.. code-block:: toml

   [logging.loggers]
   "*" = {level = "INFO", handlers = ["queue"]}

When :func:`~thinlog.configure_logging` encounters the ``"*"`` key, it copies
that configuration to every logger in the *more_loggers* list and every logger
registered in :class:`~thinlog.RegisteredLoggers`:

.. code-block:: python

   from thinlog import get_logger, configure_logging

   # Pre-register loggers across your codebase
   auth_logger = get_logger("auth", {"component": "auth"})
   db_logger = get_logger("db", {"component": "db"})

   # Later, at startup:
   log_gen = configure_logging(
       "myapp",
       config["logging"],
       include_registered_loggers=True,
       include_default_logger=True,
   )
   logger = next(log_gen)
   # Now "auth", "db", and "myapp" all have the wildcard config applied.

Merge (``"merge": true``)
--------------------------

Sometimes a specific logger needs the wildcard config *plus* some extras.
Set ``"merge": true`` on the specific logger to combine rather than replace:

.. code-block:: toml

   [logging.loggers]
   "*" = {level = "INFO", handlers = ["queue"]}

   [logging.loggers.trace_log]
   merge = true
   handlers = ["trace_handler"]

With merge, ``trace_log`` inherits ``level = "INFO"`` and ``handlers = ["queue"]``
from the wildcard, and ``"trace_handler"`` is **appended** to the handlers list.
Dicts are deep-merged; lists are extended; scalars are overwritten.

Multi-process applications
--------------------------

In multi-process setups (e.g., ``gunicorn``, ``uvicorn`` workers, Celery),
**configure logging on each worker start**, not just in the main process.
Use a :class:`~logging.handlers.QueueHandler` to offload I/O to a background
thread within each worker:

.. code-block:: toml

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "INFO", stream = "ext://sys.stderr", formatter = "msg"}
   queue = {class = "logging.handlers.QueueHandler", handlers = ["stream"], formatter = "json", respect_handler_level = true}

:func:`~thinlog.configure_logging` automatically detects the ``QueueHandler``,
starts its listener on entry, and stops it on generator exit.

Separate loggers per component
-------------------------------

A recommended pattern for microservices:

* One **application logger** (``"myapp"``) for business logic.
* One **library logger** (``"mylib"``) per internal library.
* Use the **wildcard** so all loggers share a common base config.
* Use :class:`~thinlog.handlers.JsonHTTPHandler` to group logs by category
  via HTTP headers — the ``AssignerFilter`` can set ``handlers_context`` to
  add per-logger headers (e.g., ``cat: "auth"``).

.. code-block:: python

   # In your library
   from thinlog import get_logger

   logger = get_logger("mylib.auth", {"component": "auth"})
   logger.info("Token validated", user_id=42)

Full example
------------

A production-ready configuration with formatters, handlers, filters, and a
queue:

.. code-block:: toml
   :caption: dev.toml

   [logging]
   root = {level = "INFO", handlers = ["queue"]}

   [logging.formatters]
   json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = false}
   msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}
   telegram = {"()" = "thinlog.formatters.telegram.TelegramFormatter"}

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "INFO", stream = "ext://sys.stderr", formatter = "msg"}
   http = {"()" = "thinlog.handlers.json_http.JsonHTTPHandler", level = "WARNING", formatter = "msg", settings = {url = "https://example.com/logs", headers = {token = "USERNAME:PASSWORD", cat = "context.base.microservice"}}}
   telegram = {"()" = "thinlog.handlers.telegram.TelegramHandler", level = "WARNING", formatter = "telegram", settings = {token = "BOT_TOKEN", chat_id = "-100CHATID", topic_id = 12345}}
   queue = {class = "logging.handlers.QueueHandler", handlers = ["stream", "telegram", "http"], formatter = "json", respect_handler_level = true}

.. code-block:: python

   import tomllib
   from pathlib import Path
   from thinlog import configure_logging

   config = tomllib.loads(Path("dev.toml").read_text())
   log_gen = configure_logging(
       "myapp",
       config["logging"],
       extra={"component": "api"},
       include_default_logger=True,
       include_registered_loggers=True,
   )
   logger = next(log_gen)

   logger.info("Service started")
   logger.error("Something broke", exc_info=True)

   log_gen.close()

See :doc:`filters` for adding filters to this configuration.

API reference
-------------

See :func:`~thinlog.configure_logging` in the :doc:`api`.
