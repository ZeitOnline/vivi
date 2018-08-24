import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


class Mail(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IMail)

    to = zeit.cms.content.property.ObjectPathProperty(
        '.to', zeit.content.modules.interfaces.IMail['to'])
    subject = zeit.cms.content.property.ObjectPathProperty(
        '.subject', zeit.content.modules.interfaces.IMail['subject'])
    body = zeit.cms.content.property.ObjectPathProperty(
        '.body', zeit.content.modules.interfaces.IMail['body'])
    success_message = zeit.cms.content.property.ObjectPathProperty(
        '.success_message', zeit.content.modules.interfaces.IMail[
            'success_message'])
    title = zeit.cms.content.property.ObjectPathProperty(
        '.title', zeit.content.modules.interfaces.IMail['title'])
    subtitle = zeit.cms.content.property.ObjectPathProperty(
        '.subtitle', zeit.content.modules.interfaces.IMail['subtitle'])
    email_required = zeit.cms.content.property.ObjectPathProperty(
        '.email_required', zeit.content.modules.interfaces.IMail[
            'email_required'])

    @property
    def subject_display(self):
        if not self.subject:
            return ''
        source = zeit.content.modules.interfaces.IMail['subject'].source
        return source.factory.getTitle(None, self.subject)
