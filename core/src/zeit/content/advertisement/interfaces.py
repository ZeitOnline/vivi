from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.content.image.interfaces
import zope.schema


class SupertitleSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {
        'publisher': _('Publisher offering'),
        'advertisement': _('Publisher advertisement'),
    }

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values.get(value, value)


class IAdvertisement(zeit.cms.content.interfaces.IXMLContent):

    title = zope.schema.Text(
        title=_('Title'),
        missing_value='')

    text = zope.schema.Text(
        title=_('Advertisement teaser'),
        required=False)

    button_text = zope.schema.TextLine(
        title=_('Button text'),
        required=False)

    button_color = zeit.cms.content.field.Color(
        title=_('Button color'),
        required=False)

    image = zope.schema.Choice(
        title=_('Image'),
        description=_('Drag an image group here'),
        required=False,
        source=zeit.content.image.interfaces.imageGroupSource)

    supertitle = zope.schema.Choice(
        title=_('Advertisement supertitle'),
        required=False,
        source=SupertitleSource())

    url = zope.schema.URI(title=_('Link address'))
