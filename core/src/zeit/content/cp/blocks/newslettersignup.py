import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.newslettersignup


@grok.implementer(zeit.content.cp.interfaces.INewsletterSignupBlock)
class NewsletterSignupBlock(
    zeit.content.modules.newslettersignup.NewsletterSignup, zeit.content.cp.blocks.block.Block
):
    type = 'newslettersignup'


class Factory(zeit.content.cp.blocks.block.BlockFactory):
    produces = NewsletterSignupBlock
    title = _('Newsletter Signup Block')
