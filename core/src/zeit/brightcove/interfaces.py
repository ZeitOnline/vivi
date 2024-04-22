import zope.interface


class ICMSAPI(zope.interface.Interface):
    """Brightcove CMS-API connection."""

    def get_video(id):
        """Returns the video metadata as a dict.
        If no video was found by Brightcove, returns None.
        """

    def get_video_sources(id):
        """Returns a list of dicts with data about video sources/renditions."""

    def update_video(bcvideo):
        """Updates the video metadata."""


class ISession(zope.interface.Interface):
    """Integrates ICMSAPI with the ``transaction`` module.
    Clients should call ``zeit.brightcove.session.get()`` to get the current
    thread-local Session instance, which they then can use to make changes.

    Note that the Brightcove API does not support transactions, so we muddle
    through by trying to commit last in the 2PC protocol. (This also means,
    if you update multiple videos and the first errors out, the other ones
    will NOT be updated.)
    """

    def update_video(bcvideo):
        """Updates the video metadata (on transaction commit)."""


class IRepository(zope.interface.Interface):
    """BBB legacy interface only kept around so generations don't complain."""
