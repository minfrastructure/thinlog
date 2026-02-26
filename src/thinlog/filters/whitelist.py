"""Whitelist filter -- allow log records that match specific criteria."""

import json
import logging
from typing import Any


class WhitelistFilter(logging.Filter):
    """Allow records whose name, message, or attributes match a whitelist.

    Records are checked against three criteria (any match is sufficient):

    * **by_name** -- the record's logger name.
    * **by_msg** -- the record's message (also checked inside JSON-encoded messages).
    * **by_attr** -- arbitrary record attributes; use the special value
      ``"_any_"`` to match any value for a given attribute.

    :param by_name: Logger names to allow.
    :param by_msg: Messages to allow.
    :param by_attr: Mapping of attribute names to expected values.
    """

    def __init__(
        self,
        by_name: list[str] | None = None,
        by_msg: list[str] | None = None,
        by_attr: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.allow_by_name = by_name or []
        self.allow_by_msg = by_msg or []
        self.allow_by_attr = by_attr or {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Return ``True`` if the record matches any whitelist criterion."""
        if record.name in self.allow_by_name:
            return True

        if record.msg in self.allow_by_msg:
            return True

        try:
            _data = json.loads(record.msg)

        except Exception:
            pass

        else:
            if isinstance(_data, dict):
                if _data.get("msg", None) and _data["msg"] in self.allow_by_msg:
                    return True

                if _data.get("name", None) and _data["name"] in self.allow_by_name:
                    return True

        for _attr, _val in self.allow_by_attr.items():
            if not hasattr(record, _attr):
                continue

            if str(_val) == "_any_":
                return True

            elif getattr(record, _attr) == _val:
                return True

        return False
