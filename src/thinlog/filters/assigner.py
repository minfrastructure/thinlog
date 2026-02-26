"""Assigner filter -- conditionally attach attributes to log records."""

from .whitelist import WhitelistFilter


class AssignerFilter(WhitelistFilter):
    """Assign attributes to matching records without blocking any.

    Extends :class:`~thinlog.filters.WhitelistFilter` -- if a record matches
    the whitelist criteria, the *assignments* dict is applied to the record as
    attributes.  The filter **always returns** ``True`` so no records are
    dropped.

    :param assignments: Mapping of attribute names to values that will be set
        on matching records via :func:`setattr`.
    """

    def __init__(self, assignments: dict, **kwargs):
        super().__init__(**kwargs)

        self.assignments = assignments

    def filter(self, record):
        """Apply assignments if the record matches, then always return ``True``."""
        if super().filter(record):
            self._apply(record)

        return True

    def _apply(self, record):
        """Set each key/value from :attr:`assignments` on the record."""
        for _key, _value in self.assignments.items():
            setattr(record, _key, _value)
