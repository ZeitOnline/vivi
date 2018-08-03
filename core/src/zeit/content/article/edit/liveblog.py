from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class Liveblog(zeit.content.article.edit.block.Block):

    grok.implements(zeit.content.article.edit.interfaces.ILiveblog)
    type = 'liveblog'

    blog_id = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'blogID',
        zeit.content.article.edit.interfaces.ILiveblog['blog_id'])
    version = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'version',
        zeit.content.article.edit.interfaces.ILiveblog['version'],
        use_default=True)
    collapse_preceding_content = (
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'collapse-preceding-content',
            zeit.content.article.edit.interfaces.ILiveblog[
                'collapse_preceding_content'], use_default=True))


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Liveblog
    title = _('Liveblog')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def set_lsc_default_for_liveblogs(context, event):
    if event.publishing:
        return
    for block in context.body.values():
        if zeit.content.article.edit.interfaces.ILiveblog.providedBy(block):
            zeit.cms.content.interfaces.ISemanticChange(
                context).has_semantic_change = True
            break
