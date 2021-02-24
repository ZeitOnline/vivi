import zope.interface


class IContentQuery(zope.interface.Interface):
    """Mechanism to retrieve content objects.
    Used to register named adapters for the different IArea.automatic_type's
    and article module ITopicbox.source_type's
    """

    total_hits = zope.interface.Attribute(
        'Total number of available results (only available after calling)')

    def __call__(self):
        """Returns list of content objects."""

    existing_teasers = zope.interface.Attribute(
        """Returns a set of ICMSContent objects that are already present on
        the CP in other areas and in topicboxes in articles.
        If IArea.hide_dupes is True, these should be not be repeated, and
        thus excluded from our query result.
        """)
