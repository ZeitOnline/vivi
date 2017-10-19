from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.mail
import zeit.edit.block
import zope.interface


class MailBlock(
        zeit.content.modules.mail.Mail,
        zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IMailBlock)


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'mail', _('Mail block'))
