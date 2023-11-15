from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.link.sources
import zope.schema


class TargetSource(zeit.cms.content.sources.SimpleDictSource):
    values = {'_blank': _('New window')}


class StatusCodeSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = ['301', '307']


class ILink(zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.content.interfaces.IXMLContent):
    """A type for managing links to non-local content."""

    url = zope.schema.URI(title=_('Link address'), constraint=zeit.cms.interfaces.valid_link_target)

    target = zope.schema.Choice(title=_('Target'), required=False, source=TargetSource())

    nofollow = zope.schema.Bool(title=_('set nofollow'), required=False, default=False)

    status_code = zope.schema.Choice(
        title=_('HTTP Status Code'), source=StatusCodeSource(), default='301'
    )

    keywords = zeit.cms.tagging.interfaces.Keywords(required=False, default=())

    blog = zope.schema.Choice(
        title=_('Blog'),
        source=zeit.content.link.sources.BlogSource(),
        readonly=True,
        required=False,
    )


class LinkSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'zeit.content.link'
    check_interfaces = (ILink,)


linkSource = LinkSource()
