import zope.interface


class ILookup(zope.interface.Interface):
    """Connection to the zeit.redirect service."""

    def rename(old_id, new_id):
        """Add redirect from old_id to new_id.
        If an object was renamed multiple times, all old uniqueIds point to the
        newest one.
        """

    def find(uniqueId):
        """Return new uniqueId if a redirect exists, else None."""
