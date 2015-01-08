import zope.interface


class ISitesProvider(zope.interface.Interface):
    """Sites provider

    Register an ISitesProvider as named utility to include the result of
    ``__iter__`` in the site control.

    """

    def __iter__():
        """Iterate over provided sites (ICMSContent)."""
