Quick Start
===========

Installation
------------

.. code-block:: bash

   pip install thinlog

Minimal example
---------------

The simplest way to use Thinlog is with a root-level config:

.. code-block:: toml
   :caption: config.toml

   [logging]
   root = {level = "DEBUG"}

.. code-block:: python

   import tomllib
   from pathlib import Path
   from thinlog import configure_logging

   config = tomllib.loads(Path("config.toml").read_text())
   log_gen = configure_logging("myapp", config["logging"])
   logger = next(log_gen)

   logger.info("Hello from Thinlog!")

:func:`~thinlog.configure_logging` is a **generator**.  Call ``next()`` to
obtain the logger.  When you are done, iterate past the yield (or close the
generator) to shut down listeners and flush handlers:

.. code-block:: python

   # Option A: manual
   log_gen.close()

   # Option B: exhaust the generator
   for _ in log_gen:
       pass

Console logging with StreamHandler
-----------------------------------

A slightly richer setup that logs to ``stderr``:

.. code-block:: toml
   :caption: config.toml

   [logging]
   root = {level = "DEBUG", handlers = ["stream"]}

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "DEBUG", stream = "ext://sys.stderr"}

.. code-block:: python

   import tomllib
   from pathlib import Path
   from thinlog import configure_logging

   config = tomllib.loads(Path("config.toml").read_text())
   log_gen = configure_logging("myapp", config["logging"])
   logger = next(log_gen)

   logger.info("Logged to stderr")
   logger.debug("Debug details", request_id="abc-123")

Rich handler
------------

For pretty terminal output using `Rich <https://rich.readthedocs.io/>`_:

.. code-block:: toml
   :caption: config.toml

   [logging]
   root = {level = "DEBUG", handlers = ["rich"]}

   [logging.handlers]
   rich = {"()" = "rich.logging.RichHandler", level = "DEBUG", rich_tracebacks = true, tracebacks_show_locals = true}

JSON logging with QueueHandler
------------------------------

For structured JSON output in production, use :class:`~thinlog.formatters.JsonFormatter`
behind a :class:`~logging.handlers.QueueHandler` for thread-safe, non-blocking delivery:

.. code-block:: toml
   :caption: config.toml

   [logging]
   root = {level = "DEBUG", handlers = ["queue"]}

   [logging.formatters]
   json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = true}
   msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "DEBUG", stream = "ext://sys.stderr", formatter = "msg"}
   queue = {class = "logging.handlers.QueueHandler", handlers = ["stream"], formatter = "json", respect_handler_level = true}

.. code-block:: python

   import tomllib
   from pathlib import Path
   from thinlog import configure_logging

   config = tomllib.loads(Path("config.toml").read_text())
   log_gen = configure_logging("myapp", config["logging"])
   logger = next(log_gen)

   logger.warning("Something happened", user_id=42)

   # When done — stops QueueHandler listener and flushes
   log_gen.close()

The ``QueueHandler`` offloads formatting and I/O to a background thread, keeping
the calling thread fast.  :func:`~thinlog.configure_logging` automatically
detects and starts/stops the listener.

Keyword arguments as extra fields
----------------------------------

:class:`~thinlog.KeywordFriendlyLogger` (the logger returned by
:func:`~thinlog.configure_logging`) lets you pass arbitrary keyword
arguments that become ``extra`` fields on the log record:

.. code-block:: python

   logger.info("User signed in", user_id=42, ip="10.0.0.1")
   # The record now has record.user_id = 42 and record.ip = "10.0.0.1"

This is especially useful with :class:`~thinlog.formatters.JsonFormatter`,
which serialises the entire record (including extra fields) as JSON.

Next steps
----------

* :doc:`configuration` -- wildcard loggers, merge, and multi-process patterns.
* :doc:`filters` -- whitelist, blocklist, and attribute assignment.
* :doc:`handlers` -- HTTP, Telegram, and context-print handlers.
* :doc:`formatters` -- JSON, message-only, and Telegram formatters.
