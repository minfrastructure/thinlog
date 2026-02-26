"""Blocklist filter -- reject log records that match specific criteria."""

import json
import logging


class BlocklistFilter(logging.Filter):
    """Block records whose name, message, or attributes match a blocklist.

    This is the inverse of :class:`~thinlog.filters.WhitelistFilter`.  Any
    record that matches is **rejected**; all others pass through.

    :param by_name: Logger names to block.
    :param by_msg: Messages to block.
    :param by_attr: Mapping of attribute names to values that trigger blocking.
        Use ``"_any_"`` to block on any value for a given attribute.
    """

    def __init__(self, by_name: list = None, by_msg: list = None, by_attr: dict = None, **kwargs):
        super().__init__(**kwargs)

        self.skip_by_name = by_name or []
        self.skip_by_msg = by_msg or []
        self.skip_by_attr = by_attr or {}

    def filter(self, record):
        """Return ``False`` if the record matches any blocklist criterion."""
        if record.name in self.skip_by_name:
            return False

        if record.msg in self.skip_by_msg:
            return False

        try:
            _data = json.loads(record.msg)

        except Exception:
            pass

        else:
            if isinstance(_data, dict):
                if _data.get("msg", None) and _data["msg"] in self.skip_by_msg:
                    return False

                if _data.get("name", None) and _data["name"] in self.skip_by_name:
                    return False

        for _attr, _val in self.skip_by_attr.items():
            if not hasattr(record, _attr):
                continue

            if str(_val) == "_any_":
                return False

            elif getattr(record, _attr) == _val:
                return False

        return True
