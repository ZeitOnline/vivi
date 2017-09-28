from zeit.cms.application import CONFIG_CACHE
from zeit.content.article.i18n import MessageFactory as _
import collections
import zc.sourcefactory.basic
import zeit.cms.content.field
import zeit.content.gallery.interfaces
import zeit.content.text.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.content.video.interfaces
import zeit.content.volume.interfaces
import zeit.edit.interfaces
import zope.schema
import zope.security.proxy


class IArticleArea(zeit.edit.interfaces.IArea):
    pass


class IEditableBody(IArticleArea):
    """Editable representation of an article's body."""

    def ensure_division():
        """Make sure the body contains a division.

        If there is no <division> in the body, update XML by creating a
        division for every 7 body elements and moving them into the created
        divisions.

        """


class IReadHeaderArea(zeit.edit.interfaces.IReadContainer):

    module = zope.interface.Attribute(
        'Convenience access for self.values()[0] or None')


class IWriteHeaderArea(zeit.edit.interfaces.IWriteContainer):

    def clear():
        """Delete all contained modules."""


class IHeaderArea(
        IReadHeaderArea,
        IWriteHeaderArea,
        IArticleArea):
    """Separate area for header that may contain one module."""


class IFindReplace(zope.interface.Interface):
    """Find/replace functionality for IEditableBody."""

    def replace_all(find, replace):
        """Replace the ``find`` text with ``replace`` in all text IBlocks."""


class ILayoutable(zope.interface.Interface):
    """A block with layout information."""

    layout = zope.interface.Attribute(
        "Layout should be a string, limitations etc. defined on  more specific"
        " interfaces")


class IParagraph(zeit.edit.interfaces.IBlock):
    """<p/> element."""

    text = zope.schema.Text(title=_('Paragraph-Text'))


class IUnorderedList(IParagraph):
    """<ul/> element."""


class IOrderedList(IParagraph):
    """<ol/> element."""


class IIntertitle(IParagraph):
    """<intertitle/> element."""


class BodyAwareXMLSource(zeit.cms.content.sources.XMLSource):

    def isAvailable(self, node, context):
        context = zeit.content.article.interfaces.IArticle(context, None)
        return super(BodyAwareXMLSource, self).isAvailable(node, context)


class IHTMLBlockLayout(zope.interface.Interface):

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')
    allowed_tags = zope.schema.ASCIILine(
        title=u"Space-separated list of tag names that are allowed"
        u" in this block's body (in addition to inline tags)")


class HTMLBlockLayout(object):

    def __init__(self, id, title, allowed_tags=None):
        self.id = id
        self.title = title
        self.allowed_tags = allowed_tags or []

    def __eq__(self, other):
        return zope.security.proxy.isinstance(
            other, HTMLBlockLayout) and self.id == other.id


class HTMLBlockLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'htmlblock-layout-source'
    attribute = 'id'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for node in tree.iterchildren('*'):
            if not self.isAvailable(node, context):
                continue
            g = node.get
            result.append(HTMLBlockLayout(
                g('id'), node.text, g('allowed_tags', '').split()))
        return result

    def getTitle(self, context, value):
        return value.title

    def getToken(self, context, value):
        return value.id


class IHTMLBlock(zeit.edit.interfaces.IBlock):
    """Section with title and body"""

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=HTMLBlockLayoutSource())

    title = zope.schema.TextLine(
        title=_('Title'))

    contents = zope.schema.Text(
        title=_('Contents'))


class IDivision(zeit.edit.interfaces.IBlock):
    """<division/> element"""

    teaser = zope.schema.TextLine(
        title=_('Page teaser'),
        required=False)

    number = zope.interface.Attribute(
        'The position of this division in the article body (1-based)')


class LayoutSourceBase(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]


class VideoLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'video-layout-source'
    attribute = 'id'


class IVideo(zeit.edit.interfaces.IBlock, ILayoutable):

    video = zope.schema.Choice(
        title=_('Video'),
        description=_("Drag a video here"),
        required=False,
        source=zeit.content.video.interfaces.videoOrPlaylistSource)

    video_2 = zope.schema.Choice(
        title=_('Video 2'),
        description=_("Drag a video here"),
        required=False,
        source=zeit.content.video.interfaces.videoOrPlaylistSource)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=VideoLayoutSource(),
        default=u'large',
        required=False)

    # XXX it would be nice if could somehow express that IVideo actually
    # is a kind of IReference (only it has video/video_2 instead of references)
    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'),
        required=False,
        default=True)


class IReference(zeit.edit.interfaces.IBlock):
    """A block which references another object."""

    references = zope.schema.Field(
        title=_('Referenced object.'),
        required=False)

    is_empty = zope.schema.Bool(
        title=_('true if this block has no reference; benefits XSLT'),
        required=False,
        default=True)


class ImageDisplayModeSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'image-display-mode-source'
    attribute = 'id'
    title_xpath = '/display-modes/display-mode'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(ImageDisplayModeSource, self).isAvailable(node, article)

IMAGE_DISPLAY_MODE_SOURCE = ImageDisplayModeSource()


class LegacyDisplayModeSource(zeit.cms.content.sources.XMLSource):
    """Source to map legacy attr `layout` to a corresponding `display_mode`."""

    product_configuration = 'zeit.content.article'
    config_url = 'legacy-display-mode-source'

    def getValues(self, context):
        tree = self._get_tree()
        return [(node.get('layout'), node.get('display_mode'))
                for node in tree.iterchildren('*')]

LEGACY_DISPLAY_MODE_SOURCE = LegacyDisplayModeSource()


class ImageVariantNameSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'image-variant-name-source'
    attribute = 'id'
    title_xpath = '/variant-names/variant-name'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(ImageVariantNameSource, self).isAvailable(node, article)

IMAGE_VARIANT_NAME_SOURCE = ImageVariantNameSource()


class MainImageVariantNameSource(ImageVariantNameSource):

    def _filter_values(self, template, values):
        tree = self._get_tree()
        names = [node.get('id') for node in tree.iterchildren('*')
                 if node.get('id') in values and
                 template in node.get('allowed', '').split(' ')]

        # No `allowed` attribute means allowed for all.
        if not names:
            return [node.get('id') for node in tree.iterchildren('*')
                    if node.get('id') in values and not node.get('allowed')]

        return names

    def _template(self, context):
        return '.'.join(
            filter(None, [context.template, context.header_layout]))

    def getValues(self, context):
        values = super(MainImageVariantNameSource, self).getValues(context)
        article = zeit.content.article.interfaces.IArticle(context)
        return self._filter_values(self._template(article), values)

    def get_default(self, context):
        general_default = self._get_tree().find('*[@default_for="*"]')
        value = general_default.get('id') if general_default else ''
        for node in self._get_tree().iterchildren('*'):
            default_for = node.get('default_for', '').split(' ')
            if self._template(context) in default_for:
                value = node.get('id')

        # Check if default value is allowed for this context.
        if value in self.getValues(context):
            return value
        else:
            return ''


MAIN_IMAGE_VARIANT_NAME_SOURCE = MainImageVariantNameSource()


class LegacyVariantNameSource(zeit.cms.content.sources.XMLSource):
    """Source to map legacy attr `layout` to a corresponding `variant_name`."""

    product_configuration = 'zeit.content.article'
    config_url = 'legacy-variant-name-source'

    def getValues(self, context):
        tree = self._get_tree()
        return [(node.get('layout'), node.get('variant_name'))
                for node in tree.iterchildren('*')]

LEGACY_VARIANT_NAME_SOURCE = LegacyVariantNameSource()


class IImage(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Image"),
        description=_("Drag an image group here"),
        source=zeit.content.image.interfaces.imageSource,
        required=False)

    set_manually = zope.schema.Bool(
        title=_("Edited"),
        required=False,
        default=False)

    display_mode = zope.schema.Choice(
        title=_('Display Mode'),
        source=IMAGE_DISPLAY_MODE_SOURCE,
        default=u'column-width',
        required=False)

    # Currently need default for bw compat.
    variant_name = zope.schema.Choice(
        title=_('Variant Name'),
        source=IMAGE_VARIANT_NAME_SOURCE,
        default=u'wide',
        required=False)


class IGallery(IReference):
    """block for <gallery/> tags."""

    references = zope.schema.Choice(
        title=_('Gallery'),
        description=_("Drag an image gallery here"),
        source=zeit.content.gallery.interfaces.gallerySource,
        required=False)


class InfoboxLayoutSource(BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'infobox-layout-source'
    attribute = 'id'


class IInfobox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Infobox'),
        description=_("Drag an infobox here"),
        source=zeit.content.infobox.interfaces.infoboxSource,
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=InfoboxLayoutSource(),
        required=False,
        default=u'default')


class ITimeline(IReference):
    """block for <timeline/> tags."""

    references = zope.schema.Choice(
        title=_('Infobox'),
        description=_("Drag an infobox here"),
        # XXX having a timeline content-type would be cleaner,
        # but this is a rather exotic use case, so there isn't one.
        source=zeit.content.infobox.interfaces.infoboxSource,
        required=False)


class PortraitboxLayoutSource(LayoutSourceBase):

    values = collections.OrderedDict([
        (u'short', _('short')),
        (u'wide', _('wide')),
    ])


class IPortraitbox(IReference, ILayoutable):
    """block for <infobox/> tags."""

    references = zope.schema.Choice(
        title=_('Portraitbox'),
        description=_("Drag a portraitbox here"),
        source=zeit.content.portraitbox.interfaces.portraitboxSource,
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=PortraitboxLayoutSource(),
        required=False,
        default=u'short')

    name = zope.schema.TextLine(
        title=_('First and last name'),
        required=False)

    text = zope.schema.Text(
        title=_('Text'),
        required=False)


class IAuthor(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Author"),
        description=_("Drag an author here"),
        source=zeit.cms.content.interfaces.authorSource,
        required=False)


class IVolume(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Volume"),
        description=_("Drag a volume here"),
        source=zeit.content.volume.interfaces.VOLUME_SOURCE,
        required=False)


def validate_rawxml(xml):
    if xml.tag != 'raw':
        raise zeit.cms.interfaces.ValidationError(
            _("The root element must be <raw>."))
    return True


class IRawXML(zeit.edit.interfaces.IBlock):

    xml = zeit.cms.content.field.XMLTree(
        title=_('XML source'),
        tidy_input=True,
        constraint=validate_rawxml)


class IRawText(zeit.edit.interfaces.IBlock):

    text_reference = zope.schema.Choice(
        title=_("Raw text reference"),
        source=zeit.content.text.interfaces.textSource,
        required=False)

    text = zope.schema.Text(
        title=_('Raw text'),
        required=False)


class IAudio(zeit.edit.interfaces.IBlock):

    audio_id = zope.schema.TextLine(
        title=_('Audio id'))

    expires = zope.schema.Datetime(
        title=_('Expires'),
        required=False)


class AvailableBlockLayoutSource(zeit.cms.content.sources.XMLSource):
    """
    Superclass for articleblocklayouts, which can be defined via XML
    """
    product_configuration = 'zeit.content.article'
    attribute = 'id'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(AvailableBlockLayoutSource,
                     self).isAvailable(node, article)


class CitationLayoutSource(AvailableBlockLayoutSource):

    config_url = 'citation-layout-source'

CITATION_LAYOUT_SOURCE = CitationLayoutSource()


class BoxLayoutSource(AvailableBlockLayoutSource):

    # If we want to check if the box is of a certain type (like infobox)
    # We could change this behaviour of isAvailable to check for a type as well
    # and maybe get rid of the superclass

    config_url = 'box-layout-source'

BOX_LAYOUT_SOURCE = BoxLayoutSource()


class ICitation(zeit.edit.interfaces.IBlock):

    text = zope.schema.Text(
        title=_('Citation'))

    attribution = zope.schema.TextLine(
        title=_('Attribution'),
        required=False)

    url = zope.schema.URI(
        title=_('URL'),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=CITATION_LAYOUT_SOURCE,
        default=u'default',
        required=False)


class ILiveblog(zeit.edit.interfaces.IBlock):

    blog_id = zope.schema.TextLine(
        title=_('Liveblog id'))


class ICardstack(zeit.edit.interfaces.IBlock):

    card_id = zope.schema.TextLine(
        title=_('Cardstack id'))
    is_advertorial = zope.schema.Bool(
        title=_('Advertorial?'),
        default=False)


class IQuiz(zeit.edit.interfaces.IBlock):

    quiz_id = zope.schema.TextLine(
        title=_('Quiz id'))
    adreload_enabled = zope.schema.Bool(
        title=_('Enable adreload'),
        default=True)


class IPodcast(zeit.edit.interfaces.IBlock):

    episode_id = zope.schema.TextLine(
        title=_('Podcast id'))


class IBox(zeit.edit.interfaces.IBlock):
    """
    This box is a first step to generalizing other boxes
    (infobox, portraitbox...). Another field, the body, should be added, which
    has the ability to contain other content, like additional images.
    """

    supertitle = zope.schema.TextLine(
        title=_('Supertitle'),
        description=_('Please take care of capitalisation.'),
        required=False,
        max_length=70)

    title = zope.schema.TextLine(
        title=_("Title"),
        required=False,
        max_length=70)

    subtitle = zope.schema.Text(
        title=_("Subtitle"),
        required=False
    )

    layout = zope.schema.Choice(
        title=_('Layout'),
        required=True,
        source=BOX_LAYOUT_SOURCE
    )


class IBreakingNewsBody(zope.interface.Interface):

    text = zope.schema.Text(
        title=_('Article body'),
        default=_('breaking-news-more-shortly'),
        required=False)

    article_id = zope.interface.Attribute(
        'The uniqueID of the breaking news article')
