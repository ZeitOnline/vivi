import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.video.interfaces


class DisplayModeSource(zeit.cms.content.sources.SimpleFixedValueSource):
    values = {
        'images': _('use images (automatic animation)'),
        'gallery': _('use gallery (automatic animation)'),
        'images-manual': _('use images (manual navigation)'),
        'gallery-manual': _('use gallery (manual navigation)'),
        'video': _('use video'),
    }


class IAnimation(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent,
):
    """A type for managing animated placeholders for articles."""

    article = zope.schema.Choice(
        title=_('Article'),
        source=zeit.content.article.interfaces.articleSource,
        required=True,
    )

    display_mode = zope.schema.Choice(
        title=_('Display mode'), required=True, source=DisplayModeSource()
    )

    video = zope.schema.Choice(
        title=_('Video to use for animation'),
        source=zeit.content.video.interfaces.VideoSource(),
        required=False,
    )

    images = zope.schema.Tuple(
        title=_('Images'),
        default=(),
        max_length=5,
        required=False,
        value_type=zope.schema.Choice(source=zeit.content.image.interfaces.ImageSource()),
    )

    gallery = zope.schema.Choice(
        title=_('Gallery to use for animation'),
        source=zeit.content.gallery.interfaces.gallerySource,
        required=False,
    )
