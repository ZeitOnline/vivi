from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


class ILookup(zope.interface.Interface):
    """Connection to the zeit.redirect service."""

    def rename(old_id, new_id):
        """Add redirect from old_id to new_id.
        If an object was renamed multiple times, all old uniqueIds point to the
        newest one.
        """

    def find(uniqueId):
        """Return new uniqueId if a redirect exists, else None."""


class IRenameInfo(zope.interface.Interface):
    previous_uniqueIds = zope.schema.Tuple(
        title=_('previous uniqueIds of this ICMSContent'),
        value_type=zope.schema.TextLine(),
        required=False,
        default=(),
    )
