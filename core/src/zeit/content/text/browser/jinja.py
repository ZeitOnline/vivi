import zope.component
import zope.formlib.form
import zope.interface
import zope.publisher.interfaces

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.repository.browser.adapter
import zeit.content.text.interfaces


class Display(zeit.cms.browser.form.DisplayForm):
    form_fields = zope.formlib.form.FormFields(zeit.content.text.interfaces.IJinjaTemplate)


class Edit(zeit.cms.browser.form.EditForm):
    title = _('Edit plain text')
    form_fields = zope.formlib.form.FormFields(zeit.content.text.interfaces.IJinjaTemplate)


@zope.component.adapter(
    zeit.content.text.interfaces.IJinjaTemplate, zope.publisher.interfaces.IPublicationRequest
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class ListRepresentation(zeit.cms.repository.browser.adapter.CMSContentListRepresentation):
    @property
    def title(self):
        return self.context.title
