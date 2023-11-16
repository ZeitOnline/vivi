from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.retresco.interfaces
import zope.schema


class IRawXML(
    zeit.cms.interfaces.IAsset,
    zeit.cms.content.interfaces.IXMLRepresentation,
    zeit.cms.repository.interfaces.IDAVContent,
    zeit.retresco.interfaces.ISkipEnrich,
):
    """An asset which is just raw xml."""

    title = zope.schema.TextLine(title=_('Title'))


class IUserDashboard(IRawXML):
    """Marker interface for the dashboard config file at ``/konto``,
    so zeit.web can register a special view for it.

    We do need to declare this in vivi, so it can de/serialize the interface.
    """
