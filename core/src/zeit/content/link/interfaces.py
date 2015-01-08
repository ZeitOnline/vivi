"""Interface definitions for the link content type."""

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zeit.cms.content.interfaces
import zope.schema


class TargetSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {'_blank': _('New window')}

    def getValues(self):
        return ('_blank',)

    def getTitle(self, value):
        return self.values.get(value, value)


class ILink(zeit.cms.content.interfaces.ICommonMetadata,
            zeit.cms.content.interfaces.IXMLContent):
    """A type for managing links to non-local content."""

    url = zope.schema.URI(title=_(u"Link address"))

    target = zope.schema.Choice(
        title=_('Target'),
        required=False,
        source=TargetSource())

    nofollow = zope.schema.Bool(
        title=_('set nofollow'),
        required=False,
        default=False)

    keywords = zeit.cms.tagging.interfaces.Keywords(
        required=False,
        default=())
