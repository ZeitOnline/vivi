from zeit.cms.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.formlib.form


class EditBox(zeit.edit.browser.view.EditBox):

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        result = super().handle_edit_action.success(data)
        self.close = False
        return result
