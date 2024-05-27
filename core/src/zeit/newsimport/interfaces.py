import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _


class IDPA(zope.interface.Interface):
    """DPA-API connection"""

    def get_entries():
        """Get all entries from dpa profile queue"""

    def delete_entries(receipts):
        """Delete entries from dpa profile by list of receipts"""


class IDPANews(zope.interface.Interface):
    urn = zope.schema.TextLine(
        title=_('urn'),  # NOTE called doc-id before
        required=True,
    )
    version = zope.schema.Int(title=_('version'), required=True)
    pubstatus = zope.schema.TextLine(  # "usable", "withheld" or "canceled"
        title=_('Publication status'), required=True
    )
    updated = zope.schema.Datetime(title=_('Timestamp update entry'), required=False)
