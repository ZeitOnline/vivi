from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.browser.form
import zeit.content.cp.interfaces
import zope.interface


class AddForm(zeit.content.cp.browser.form.AddForm):

    title = _("Add storystream")

    def create(self, data):
        obj = super(AddForm, self).create(data)
        obj.type = u'storystream'  # XXX Hard-coding this is a bit shaky.
        zope.interface.alsoProvides(
            obj, zeit.content.cp.interfaces.IStoryStream)
        return obj
