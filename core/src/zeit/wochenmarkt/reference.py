import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.author.interfaces


@grok.adapter(zeit.wochenmarkt.interfaces.IIngredients, name='ingredients')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    node = lxml.objectify.E.author(
        href=context.uniqueId, hdok=context.honorar_id or '')
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node
