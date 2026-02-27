# Thinlog

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/thinlog.svg)](https://pypi.org/project/thinlog/)
[![License](https://img.shields.io/pypi/l/thinlog.svg)](https://pypi.org/project/thinlog/)
[![Typed](https://img.shields.io/badge/typing-strict-green.svg)](https://mypy.readthedocs.io/)

A lightweight, fully-typed Python logging toolkit — a thin wrapper on the standard `logging` library with extra wheels.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Concepts](#concepts)
  - [Structured Log Keys](#structured-log-keys)
  - [configure\_logging](#configure_logging)
  - [Wildcard Loggers](#wildcard-loggers)
  - [Filters](#filters)
  - [Handlers](#handlers)
  - [Formatters](#formatters)
- [Documentation](#documentation)

## Features

- **Wildcard logger configuration** — define a `"*"` logger and have it applied to every registered logger.
- **Keyword-friendly logging** — pass keyword arguments directly; they become `extra` fields.
- **Advanced filters** — whitelist, blocklist, and conditional attribute assignment via TOML config.
- **Structured JSON output** — rich exception context powered by [structlog](https://www.structlog.org/).
- **Remote logging** — send logs to an HTTP endpoint or Telegram chat out of the box.
- **Fully typed** — strict MyPy compliance with a `py.typed` PEP 561 marker.

## Installation

```bash
pip install thinlog
```

## Quick Start

**config.toml:**

```toml
[logging]
root = {level = "DEBUG", handlers = ["queue"]}

[logging.formatters]
json = {"()" = "thinlog.formatters.json.JsonFormatter", show_locals = false}
msg = {"()" = "thinlog.formatters.msg.MsgFormatter"}

[logging.handlers]
stream = {class = "logging.StreamHandler", level = "DEBUG", stream = "ext://sys.stderr", formatter = "msg"}
queue = {class = "logging.handlers.QueueHandler", handlers = ["stream"], formatter = "json", respect_handler_level = true}
```

**app.py:**

```python
import tomllib
from pathlib import Path
from thinlog import configure_logging

config = tomllib.loads(Path("config.toml").read_text())
logger = configure_logging("myapp", config["logging"])

logger.info("app_started")
logger.warning("processing_payment_failed", user_id=42, ip="10.0.0.1")
```

From any other component or file if you need a specific logger you can simply do:
```python
from thinlog import get_logger

logger = get_logger("my_other_specific_logger", dict(more="data", we="can pass"))

# Rest of the file...
```

> **A recommendation**: Context(ctx) is good, use context everywhere, your app can have its own context, every request can
> have its own ctx so you can easily access your resources(e.g myapp logger) from ctx.

## Concepts

### Structured Log Keys

Thinlog treats the first argument of a log call as a **machine-readable key**, not a human-readable sentence. Use lowercase, underscore-separated identifiers that describe the event:

```python
# Preferred — a stable, searchable key
logger.error("payment_gateway_timeout", order_id=512, gateway="stripe")

# Avoid — a free-form sentence that is hard to filter or aggregate
logger.error("The payment gateway timed out while processing order 512")
```

Structured keys are easy to match with filters, trivial to `GROUP BY` in a log aggregation system, and never require fragile regular expressions to parse. Pair them with keyword arguments for all variable data and you get logs that are both compact and rich in context.

Since this library is optimized so that each component have its own logger, the `key` can be short and optimized.
```python
from thinlog import get_logger

logger = get_logger("my_other_specific_logger", dict(more="data", we="can pass"))
logger.error("request_failed", id=2)
# If there are multiple loggers with the key set to `request_failed`, it won't conflict.
# since it belongs to `my_other_specific_logger`, 
# we can easily find the cause and easily filterable in logging stacks.
```

### configure\_logging

`configure_logging` is a plain function that returns a ready-to-use logger. It registers an `atexit` handler that automatically stops QueueHandler listeners and flushes handlers on interpreter exit.

### Wildcard Loggers

Define a `"*"` logger in your config and it will be applied to all registered loggers. Use `"merge": true` on a specific logger to extend rather than replace the wildcard config.

```toml
[logging.loggers]
"*" = {level = "INFO", handlers = ["queue"]}

[logging.loggers.trace_log]
merge = true
handlers = ["trace_handler"]
```

### Filters

- **WhitelistFilter** — allow records matching name, message, or attribute patterns.
- **BlocklistFilter** — block matching records (inverse of whitelist).
- **AssignerFilter** — conditionally assign attributes to matching records without blocking any.

```toml
[logging.filters]
skip_noisy = {"()" = "thinlog.filters.blocklist.BlocklistFilter", by_name = ["urllib3", "httpx"]}
```

### Handlers

- **JsonHTTPHandler** — send JSON logs via HTTP POST with per-record URL/header overrides.
- **TelegramHandler** — send logs to Telegram; auto-splits long messages into document attachments.
- **CtxPrintHandler** — print record context as JSON to stdout for development.

### Formatters

- **JsonFormatter** — full record as JSON with structured exception tracebacks.
- **MsgFormatter** — plain message string only.
- **TelegramFormatter** — HTML-formatted output with length-aware splitting.

## Documentation

Full documentation is available at [minfrastructure.github.io/thinlog](https://minfrastructure.github.io/thinlog).

This module is fully typed and compatible with [MyPy](https://mypy.readthedocs.io/en/stable/) out of the box. Please open an [issue](https://github.com/minfrastructure/thinlog/issues) for any suggestions or bugs.
