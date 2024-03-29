import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.content.image.interfaces


class IPortraitbox(zeit.cms.content.interfaces.IXMLContent):
    name = zope.schema.TextLine(title=_('First and last name'))

    text = zeit.cms.content.field.XMLTree(title=_('Text'))

    image = zope.schema.Choice(
        title=_('Image'), source=zeit.content.image.interfaces.imageSource, required=False
    )


class PortraitboxSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'zeit.content.portraitbox'
    check_interfaces = (IPortraitbox,)


portraitboxSource = PortraitboxSource()


class IPortraitboxReference(zope.interface.Interface):
    portraitbox = zope.schema.Choice(
        title=_('Portraitbox'), required=False, source=portraitboxSource
    )
