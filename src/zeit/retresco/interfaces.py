import zope.interface


class ITMS(zope.interface.Interface):
    """The retresco topic management system."""

    def get_keywords(content):
        """Analyzes the given ICMSContent and returns a list of
        zeit.cms.tagging.interfaces.ITag objects."""
