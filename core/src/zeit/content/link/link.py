from zeit.cms.content.dav import DAVProperty
from zeit.cms.content.property import ObjectPathProperty, SwitchableProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.link.interfaces import ILink
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


NS = 'http://namespaces.zeit.de/CMS/link'


@zope.interface.implementer(
    zeit.content.link.interfaces.ILink,
    zeit.cms.interfaces.IEditorialContent)
class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    default_template = (
        '<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></link>')

    url = SwitchableProperty(
        DAVProperty(ILink['url'], NS, 'url'),
        ObjectPathProperty('.body.url'))
    target = SwitchableProperty(
        DAVProperty(ILink['target'], NS, 'target'),
        ObjectPathProperty('.body.target'))
    nofollow = SwitchableProperty(
        DAVProperty(ILink['nofollow'], NS, 'nofollow'),
        ObjectPathProperty('.body.nofollow'))
    status_code = SwitchableProperty(
        DAVProperty(ILink['status_code'], NS, 'status_code'),
        ObjectPathProperty(
            '.body.status', ILink['status_code'], use_default=True))

    @property
    def blog(self):
        if not self.url:
            return
        source = zeit.content.link.interfaces.ILink['blog'].source(self)

        for blog in source:
            if blog.url in self.url:
                return blog

    @property
    def title(self):
        return self.teaserTitle

    @title.setter
    def title(self, value):
        self.teaserTitle = value


class LinkType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Link
    interface = zeit.content.link.interfaces.ILink
    title = _('Link')
    type = 'link'


@zope.component.adapter(zeit.content.link.interfaces.ILink)
class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

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
