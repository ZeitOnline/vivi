from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.repository.browser.adapter
import zeit.content.text.interfaces
import zope.component
import zope.formlib.form
import zope.interface
import zope.publisher.interfaces


class Edit(zeit.cms.browser.form.EditForm):

    title = _('Edit plain text')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IJinjaTemplate)


class ListRepresentation(
        zeit.cms.repository.browser.adapter.CMSContentListRepresentation):

    zope.component.adapts(
        zeit.content.text.interfaces.IJinjaTemplate,
        zope.publisher.interfaces.IPublicationRequest)
    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)

    @property
    def title(self):
        return self.context.title
