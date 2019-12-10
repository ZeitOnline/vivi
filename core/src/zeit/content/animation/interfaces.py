from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.content.video.interfaces
import zeit.content.article.interfaces
import zope.schema


class DisplayModeSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {"images": _("use images"), "video": _("use video")}

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values.get(value, value)


class IAnimation(
    zeit.cms.content.interfaces.ICommonMetadata, zeit.cms.content.interfaces.IXMLContent
):
    """A type for managing animated placeholders for articles."""

    article = zope.schema.Choice(
        title=_("Article"),
        source=zeit.cms.content.contentsource.cmsContentSource,
        required=True,
    )

    display_mode = zope.schema.Choice(
        title=_("Display mode"), required=False, source=DisplayModeSource()
    )

    video = zope.schema.Choice(
        title=_("Video to use for animation"),
        source=zeit.content.video.interfaces.VideoSource(),
        required=False,
    )

    images = zope.schema.Tuple(
        title=_('Images'),
        default=(),
        max_length=3,
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.content.image.interfaces.ImageSource()))
