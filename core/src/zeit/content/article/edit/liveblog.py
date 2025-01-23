import grokcore.component as grok
import zope.component

from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import ITickarooLiveblog
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.modules.interfaces
import zeit.content.modules.liveblog


@grok.subscribe(
    zeit.content.article.interfaces.IArticle, zeit.cms.checkout.interfaces.IAfterCheckoutEvent
)
def set_lsc_default_for_liveblogs(context, event):
    if event.publishing:
        return
    for block in context.body.values():
        if zeit.content.article.edit.interfaces.ITickarooLiveblog.providedBy(block):
            zeit.cms.content.interfaces.ISemanticChange(context).has_semantic_change = True
            break


@grok.implementer(zeit.content.article.edit.interfaces.ITickarooLiveblog)
class TickarooLiveblog(
    zeit.content.article.edit.block.Block, zeit.content.modules.liveblog.TickarooLiveblog
):
    type = 'tickaroo_liveblog'


@zope.component.adapter(ITickarooLiveblog)
class TickarooLiveblogFactory(zeit.content.article.edit.block.BlockFactory):
    produces = TickarooLiveblog
    title = _('Tickaroo liveblog block')
