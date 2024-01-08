import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.mail


@grok.implementer(zeit.content.article.edit.interfaces.IMail)
class Mail(zeit.content.modules.mail.Mail, zeit.content.article.edit.block.Block):
    type = 'mail'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = Mail
    title = _('Mail block')
