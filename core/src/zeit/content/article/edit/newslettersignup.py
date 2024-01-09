import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.newslettersignup


@grok.implementer(zeit.content.article.edit.interfaces.INewsletterSignup)
class NewsletterSignup(
    zeit.content.modules.newslettersignup.NewsletterSignup, zeit.content.article.edit.block.Block
):
    type = 'newslettersignup'


class NewsletterSignupBlockFactory(zeit.content.article.edit.block.BlockFactory):
    produces = NewsletterSignup
    title = _('Newsletter Signup block')
