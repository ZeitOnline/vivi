from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.mail
import zeit.edit.block


class Mail(
        zeit.content.modules.mail.Mail,
        zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(zeit.content.article.edit.interfaces.IMail)
    type = 'mail'


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Mail
    title = _('Mail block')
