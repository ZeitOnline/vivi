from zeit.cms.i18n import MessageFactory as _
import zope.formlib.interfaces
import zope.interface


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class DuplicateAuthorWarning(Exception):

    def doc(self):
        return _(
            u'An author with the given name already exists. '
            u'If you\'d like to create another author with the same '
            u'name anyway, check "Add duplicate author" '
            u'and save the form again.')
