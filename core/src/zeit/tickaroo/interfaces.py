import zope.interface


class ILiveblogTimeline(zope.interface.Interface):
    """Connection to the Tickaroo liveblog API."""

    def get_events(liveblog_id):
        pass
