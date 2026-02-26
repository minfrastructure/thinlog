Filters
=======

Thinlog ships three configurable filters that cover the most common
filtering and enrichment patterns.  They can all be configured directly
in TOML via ``dictConfig``'s ``"()"`` syntax.

WhitelistFilter
---------------

:class:`~thinlog.filters.WhitelistFilter` **allows** records that match at
least one criterion and rejects everything else.

See :class:`~thinlog.filters.WhitelistFilter` in the :doc:`api`.

**TOML example** — only allow records from ``"payments"`` or with the message
``"health_check"``:

.. code-block:: toml

   [logging.filters]
   allow_payments = {"()" = "thinlog.filters.whitelist.WhitelistFilter", by_name = ["payments"], by_msg = ["health_check"]}

**Attribute matching** with ``_any_`` wildcard — allow any record that has a
``request_id`` attribute, regardless of its value:

.. code-block:: toml

   [logging.filters]
   has_request = {"()" = "thinlog.filters.whitelist.WhitelistFilter", by_attr = {request_id = "_any_"}}

**JSON-encoded messages** — if the log message is a JSON string, the filter
also checks its ``"msg"`` and ``"name"`` keys.

BlocklistFilter
---------------

:class:`~thinlog.filters.BlocklistFilter` is the inverse of
:class:`~thinlog.filters.WhitelistFilter`.  Records that match are
**rejected**; everything else passes through.

See :class:`~thinlog.filters.BlocklistFilter` in the :doc:`api`.

**TOML example** — suppress records from ``"trace_log"`` and
``"noisy_library"``:

.. code-block:: toml

   [logging.filters]
   skip_noisy = {"()" = "thinlog.filters.blocklist.BlocklistFilter", by_name = ["trace_log", "noisy_library"]}

AssignerFilter
--------------

:class:`~thinlog.filters.AssignerFilter` extends
:class:`~thinlog.filters.WhitelistFilter` — when a record matches, attributes
from the *assignments* dict are set on the record.  The filter **always returns
True** so no records are dropped.

See :class:`~thinlog.filters.AssignerFilter` in the :doc:`api`.

**TOML example** — tag ``"trace_log"`` records with a custom HTTP header for
:class:`~thinlog.handlers.JsonHTTPHandler`:

.. code-block:: toml

   [logging.filters.assign_tracelog]
   "()" = "thinlog.filters.assigner.AssignerFilter"
   by_name = ["trace_log"]
   assignments = {handlers_context = {json_http = {append_headers = {cat = "trace"}}}}

Custom context filters
-----------------------

For application-specific enrichment (e.g., attaching request data or base
context), write a simple :class:`logging.Filter` subclass.  Here are two
common patterns:

**RequestDataContextFilter** — attach per-request data from a
:class:`~contextvars.ContextVar`:

.. code-block:: python

   import logging
   from contextvars import ContextVar
   from typing import Optional


   class RequestData:
       current_context: ContextVar["RequestData"] = ContextVar("request_data")

       @classmethod
       def current(cls) -> Optional["RequestData"]:
           return cls.current_context.get(None)

       @property
       def ip(self) -> str:
           return "127.0.0.1"  # e.g., self.request.client.host

       def dict(self) -> dict:
           return {"ip": self.ip}


   class RequestDataContextFilter(logging.Filter):
       def filter(self, record):
           rd = RequestData.current()
           if not rd:
               return True

           if not hasattr(record, "context"):
               record.context = {}

           record.context["request_data"] = rd.dict()
           return True

**BaseContextFilter** — attach static application context (app ID,
microservice name):

.. code-block:: python

   import logging
   from types import SimpleNamespace
   from typing import ClassVar, Self


   class BaseContext(SimpleNamespace):
       _instance: ClassVar[Self]
       app_id = "some_id"
       pkg = "some_package"

       def __init__(self, **kwargs):
           super().__init__(**kwargs)
           self.__class__._instance = self

       @classmethod
       def instance(cls):
           try:
               return cls._instance
           except AttributeError:
               return cls()


   class BaseContextFilter(logging.Filter):
       def filter(self, record):
           ctx = BaseContext.instance()

           if not hasattr(record, "context"):
               record.context = {}

           record.context["base"] = dict(app_id=ctx.app_id, microservice=ctx.pkg)
           return True

These filters are referenced in TOML via their fully-qualified class path:

.. code-block:: toml

   [logging.filters]
   request_data = {"()" = "myapp.filters.RequestDataContextFilter"}
   base_context = {"()" = "myapp.filters.BaseContextFilter"}

Complete example with filters
------------------------------

A production configuration using all filter types:

.. code-block:: toml
   :caption: dev.toml

   [logging]
   root = {level = "INFO", handlers = ["queue"]}

   [logging.formatters]
   json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = false}
   msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}
   telegram = {"()" = "thinlog.formatters.telegram.TelegramFormatter"}

   [logging.filters]
   request_data = {"()" = "myapp.filters.RequestDataContextFilter"}
   base_context = {"()" = "myapp.filters.BaseContextFilter"}
   skip_tracelog = {"()" = "thinlog.filters.blocklist.BlocklistFilter", by_name = ["trace_log"]}

   [logging.filters.assign_tracelog]
   "()" = "thinlog.filters.assigner.AssignerFilter"
   by_name = ["trace_log"]
   assignments = {handlers_context = {json_http = {append_headers = {cat = "trace"}}}}

   [logging.handlers]
   stream = {class = "logging.StreamHandler", level = "INFO", stream = "ext://sys.stderr", filters = ["skip_tracelog"], formatter = "msg"}
   queue = {class = "logging.handlers.QueueHandler", filters = ["request_data", "base_context"], handlers = ["stream", "telegram", "http"], formatter = "json", respect_handler_level = true}

   [logging.handlers.http]
   "()" = "thinlog.handlers.json_http.JsonHTTPHandler"
   level = "WARNING"
   filters = ["assign_tracelog"]
   formatter = "msg"
   settings = {url = "https://example.com/logs", headers = {token = "USERNAME:PASSWORD", cat = "context.base.microservice"}}

   [logging.handlers.telegram]
   "()" = "thinlog.handlers.telegram.TelegramHandler"
   filters = ["skip_tracelog"]
   level = "WARNING"
   formatter = "telegram"
   settings = {token = "BOT_TOKEN", chat_id = "-100CHATID", topic_id = 12345}

The flow:

1. All records pass through ``request_data`` and ``base_context`` filters at
   the **queue** level, enriching them with context.
2. The **stream** handler uses ``skip_tracelog`` to suppress ``trace_log`` records.
3. The **http** handler uses ``assign_tracelog`` to add a custom ``cat`` header
   for ``trace_log`` records, grouping them separately on the server.
4. The **telegram** handler also uses ``skip_tracelog`` to keep the chat clean.

Common patterns
----------------

**Skip noisy third-party loggers:**

.. code-block:: toml

   [logging.filters]
   skip_noisy = {"()" = "thinlog.filters.blocklist.BlocklistFilter", by_name = ["urllib3", "httpx", "asyncio"]}

**Assign HTTP headers by logger category** for
:class:`~thinlog.handlers.JsonHTTPHandler`:

.. code-block:: toml

   [logging.filters.assign_auth]
   "()" = "thinlog.filters.assigner.AssignerFilter"
   by_name = ["auth"]
   assignments = {handlers_context = {json_http = {append_headers = {cat = "auth"}}}}

   [logging.filters.assign_billing]
   "()" = "thinlog.filters.assigner.AssignerFilter"
   by_name = ["billing"]
   assignments = {handlers_context = {json_http = {append_headers = {cat = "billing"}}}}
