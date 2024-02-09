import copy

import grokcore.component as grok
import lxml.builder
import zope.security.proxy

import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.author.interfaces


@grok.adapter(zeit.content.author.interfaces.IAuthor, name='author')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def XMLReference(context):
    node = lxml.builder.E.author(href=context.uniqueId, hdok=context.honorar_id or '')
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    target_iface = zeit.content.author.interfaces.IAuthor

    def update_with_context(self, node, context):
        node.display_name = context.display_name


class AuthorshipXMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    target_iface = zeit.cms.content.interfaces.ICommonMetadata

    def update_with_context(self, node, context):
        for author in node.findall('author'):
            node.remove(author)
        for reference in context.authorships:
            node.append(copy.copy(zope.security.proxy.getObject(reference.xml)))
        # BBB The ``author`` attribute is deprecated in favor of the <author>
        # tags, but XSLT and mobile still use it.
        try:
            legacy_author = ';'.join([x.target.display_name for x in context.authorships])
            node.attrib.pop('author', None)
            if context.authorships:
                node.set('author', legacy_author)
        except Exception:
            # We've sometimes seen data errors with Friedbert where authors
            # don't have a type (and thus no ``display_name``), see VIV-629.
            if not self.suppress_errors:
                raise


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
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(node)
    return node


@grok.implementer(zeit.content.author.interfaces.IAuthorBioReference)
class RelatedReference(zeit.cms.content.reference.Reference):
    grok.adapts(zeit.content.article.edit.interfaces.IAuthor, zeit.cms.interfaces.IXMLElement)
    grok.provides(zeit.cms.content.interfaces.IReference)
    grok.name('related')

    biography = zeit.cms.content.property.ObjectPathProperty('.biography')
