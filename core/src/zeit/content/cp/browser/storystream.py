from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.browser.form
import zeit.content.cp.interfaces
import zope.interface


class AddForm(zeit.content.cp.browser.form.AddForm):

    title = _("Add storystream")
    form_fields = zeit.content.cp.browser.form.AddForm.form_fields.omit('type')

    def create(self, data):
        obj = super(AddForm, self).create(data)
        obj.type = 'storystream'  # XXX Hard-coding this is a bit shaky.
        zope.interface.alsoProvides(
            obj, zeit.content.cp.interfaces.IStoryStream)
        return obj
