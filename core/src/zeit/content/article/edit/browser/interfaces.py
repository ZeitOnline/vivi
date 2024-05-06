import zope.formlib.interfaces
import zope.interface

from zeit.cms.i18n import MessageFactory as _


class IFoldable(zope.interface.Interface):
    """Marker interface for a block which can be callapsed."""


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class VideoTagesschauNoResultError(Exception):
    def __init__(self, error_type):
        self.error_type = error_type

    def doc(self):
        return {
            'empty': _('No tagesschau video recommendation found.'),
            'technical': _('Error while requesting API or processing recommendations'),
        }[self.error_type]
