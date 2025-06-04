import zope.interface


class IJson(zope.interface.Interface):
    """Downloads the teaser splittest configuration from Sourcepoint and stores
    it in DAV, so zeit.web can serve it.

    Supports periodically checking/downloading a new version; each version is
    offered under its own URL, so we can set a very long Cache-Control header
    for clients.
    """

    latest_version = zope.interface.Attribute(
        'ICMSContent representing the latest locally stored version'
    )

    def update():
        """Downloads the current version from Kilkaya.
        If its contents are different from our `latest_version`, a new
        version is created and stored in DAV.
        """

    def sweep(keep):
        """Removes old versions from DAV, keeping the given number of most
        recent ones.
        """
