Thinlog
=======

**Thinlog** is a lightweight, fully-typed Python logging toolkit that extends the
standard :mod:`logging` library with extra wheels:

* **Wildcard logger configuration** -- define a single ``"*"`` logger and have it
  applied to every registered logger automatically.
* **Keyword-friendly logging** -- pass keyword arguments directly; they become
  ``extra`` fields on the log record.
* **Advanced filters** -- whitelist, blocklist, and conditional attribute
  assignment without writing custom filter classes.
* **Structured JSON output** -- rich exception context powered by
  `structlog <https://www.structlog.org/>`_.
* **Remote logging** -- send logs to an HTTP endpoint or a Telegram chat
  out of the box.
* **Fully typed** -- strict MyPy compliance with a ``py.typed`` PEP 561 marker.

Getting started
---------------

Install from PyPI:

.. code-block:: bash

   pip install thinlog

Then head over to the :doc:`quickstart` to see Thinlog in action.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   configuration
   filters
   handlers
   formatters
   api
