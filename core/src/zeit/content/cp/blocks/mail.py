from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.mail


class MailBlock(
        zeit.content.modules.mail.Mail,
        zeit.content.cp.blocks.block.Block):

    grok.implements(zeit.content.cp.interfaces.IMailBlock)
    type = 'mail'


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = MailBlock
    title = _('Mail block')
