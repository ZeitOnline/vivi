import grokcore.component as grok
import zope.component
import zope.interface

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.link.interfaces
import zeit.push.interfaces


@zope.interface.implementer(
    zeit.content.link.interfaces.ILink, zeit.cms.interfaces.IEditorialContent
)
class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    default_template = '<link><head/><body/></link>'

    url = zeit.cms.content.property.ObjectPathProperty('.body.url')
    target = zeit.cms.content.property.ObjectPathProperty('.body.target')
    nofollow = zeit.cms.content.property.ObjectPathProperty('.body.nofollow')
    status_code = zeit.cms.content.property.ObjectPathProperty(
        '.body.status', zeit.content.link.interfaces.ILink['status_code'], use_default=True
    )

    @property
    def blog(self):
        if not self.url:
            return None
        source = zeit.content.link.interfaces.ILink['blog'].source(self)
        for blog in source:
            if blog.url in self.url:
                return blog
        return None

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


@grok.adapter(zeit.content.link.interfaces.ILink)
@grok.implementer(zeit.push.interfaces.IPushURL)
def link_push_url(context):
    return context.url
