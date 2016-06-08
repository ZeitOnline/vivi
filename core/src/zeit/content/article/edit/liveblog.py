from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


class Liveblog(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.implements(zeit.content.article.edit.interfaces.ILiveblog)
    type = 'liveblog'

    blog_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'blogID',
        zeit.content.article.edit.interfaces.ILiveblog['blog_id'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Liveblog
    title = _('Liveblog')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def set_lsc_default_for_liveblogs(context, event):
    if event.publishing:
        return
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    for block in body.values():
        if zeit.content.article.edit.interfaces.ILiveblog.providedBy(block):
            zeit.cms.content.interfaces.ISemanticChange(
                context).has_semantic_change = True
            break
