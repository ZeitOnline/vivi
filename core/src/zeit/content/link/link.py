
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.link.interfaces
import zeit.push.interfaces
import zope.component
import zope.interface


class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    zope.interface.implements(zeit.content.link.interfaces.ILink,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = (
        '<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></link>')

    url = zeit.cms.content.property.ObjectPathProperty('.body.url')
    target = zeit.cms.content.property.ObjectPathProperty('.body.target')
    nofollow = zeit.cms.content.property.ObjectPathProperty('.body.nofollow')

    @property
    def blog(self):
        sources = zeit.content.link.interfaces.ILink['blog'].source
        for source in sources:
            if source.url in self.target:
                return source


class LinkType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Link
    interface = zeit.content.link.interfaces.ILink
    title = _('Link')
    type = 'link'


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the expire/publication time to feed entry."""

    zope.component.adapts(zeit.content.link.interfaces.ILink)

    def update(self, entry, suppress_errors=False):
        url = self.context.url
        if not url:
            url = ''
        entry.set('{http://namespaces.zeit.de/CMS/link}href', url)

        target_attribute = '{http://namespaces.zeit.de/CMS/link}target'
        if self.context.target:
            entry.set(target_attribute, self.context.target)
        else:
            entry.attrib.pop(target_attribute, None)

        rel_attribute = '{http://namespaces.zeit.de/CMS/link}rel'
        if self.context.nofollow:
            entry.set(rel_attribute, 'nofollow')
        else:
            entry.attrib.pop(rel_attribute, None)


@grok.adapter(zeit.content.link.interfaces.ILink)
@grok.implementer(zeit.push.interfaces.IPushURL)
def link_push_url(context):
    return context.url
