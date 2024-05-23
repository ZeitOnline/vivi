import grokcore.component as grok
import lxml.builder

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.author.interfaces


@grok.adapter(zeit.content.author.interfaces.IAuthor, name='author')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    node = lxml.builder.E.author(href=context.uniqueId, hdok=context.honorar_id or '')
    return node


@grok.implementer(zeit.content.author.interfaces.IAuthorReference)
class Reference(zeit.cms.content.reference.Reference):
    grok.provides(zeit.content.author.interfaces.IAuthorReference)
    grok.name('author')

    location = zeit.cms.content.property.ObjectPathProperty('.location')
    role = zeit.cms.content.property.ObjectPathProperty('.role')


@grok.adapter(zeit.content.author.interfaces.IAuthor, name='related')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLRelatedReference(context):
    node = lxml.builder.E.author(href=context.uniqueId)
    return node


@grok.implementer(zeit.content.author.interfaces.IAuthorBioReference)
class RelatedReference(zeit.cms.content.reference.Reference):
    grok.adapts(zeit.content.article.edit.interfaces.IAuthor, zeit.cms.interfaces.IXMLElement)
    grok.provides(zeit.cms.content.interfaces.IReference)
    grok.name('related')

    biography = zeit.cms.content.property.ObjectPathProperty('.biography')
