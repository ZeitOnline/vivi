from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.edit.browser.view
import zope.browserpage
import zope.formlib.form


class EditBox(zeit.edit.browser.view.EditBox):
    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        result = super().handle_edit_action.success(data)
        self.close = False
        return result


# XXX this cobbles together just enough to combine SubPageForm and GroupedForm
class GroupedSubpageForm(
    zope.formlib.form.SubPageEditForm,
    zeit.cms.browser.form.WidgetCSSMixin,
    gocept.form.grouped.EditForm,
):
    field_groups = NotImplemented

    widget_groups = ()

    close = False

    template = zope.browserpage.ViewPageTemplateFile('grouped-subpageform.pt')

    @property
    def form(self):
        return ''  # our template uses the grouped-form macros instead
