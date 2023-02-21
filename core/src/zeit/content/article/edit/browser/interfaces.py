from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.formlib.interfaces


class IFoldable(zope.interface.Interface):
    """Marker interface for a block which can be callapsed."""


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class VideoTagesschauNoResultError(Exception):

    def __init__(self, error_type):
        self.error_type = error_type

    def doc(self):
        return {
            'empty': _('No tagesschau video recommendation found.'),
            'technical': _('Error while requesting tagesschau API'),
        }[self.error_type]
