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


class IHeaderArea(IArticleArea):
    """Separate area for header that may contain one module."""

    module = zope.interface.Attribute(
        'Convenience access for self.values()[0] or None')


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

IMAGE_VARIANT_NAME_SOURCE = ImageVariantNameSource()


class MainImageVariantNameSource(ImageVariantNameSource):

    def _filter_values(self, template_context, values):
        tree = self._get_tree()
        names = [node.get('id') for node in tree.iterchildren('*')
                 if node.get('allowed') and (
                 template_context in node.get('allowed').split(" ")) and (
                 node.get('id')) in values]

        # We need to determine the names for empty names or no template context.
        # We define: No explicit allowed attribute is implicitly resolved to
        # allowed for all.
        if not names or not template_context:
            return [node.get('id') for node in tree.iterchildren('*')
                    if not node.get('allowed') and node.get('id') in values]

        return names

    def _template_context(self, context):
        template = context.template if context.template else ''
        layout = context.header_layout if context.header_layout else ''
        return '{}.{}'.format(template, layout).strip('.')

    def getValues(self, context):
        values = super(MainImageVariantNameSource, self).getValues(context)
        article = zeit.content.article.interfaces.IArticle(context)
        return self._filter_values(self._template_context(article), values)

    def get_default(self, context):
        value = self._get_tree().find(
            'variant-name[@default_for="*"]').get('id')

        for node in self._get_tree().iterchildren('*'):
            default_for = node.get('default_for', '').split(" ")
            if self._template_context(context) in default_for:
                value = node.get('id')

        # Check, if default value is allowed for this context
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
        default=u'large',
        required=False)

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


class IAuthor(IReference):

    references = zeit.cms.content.interfaces.ReferenceField(
        title=_("Author"),
        description=_("Drag an author here"),
        source=zeit.cms.content.interfaces.authorSource,
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


class CitationLayoutSource(LayoutSourceBase):

    values = collections.OrderedDict([
        (u'short', _('short')),
        (u'wide', _('wide')),
        (u'double', _('double')),
    ])


class ICitation(zeit.edit.interfaces.IBlock):

    text = zope.schema.Text(
        title=_('Citation'))

    attribution = zope.schema.TextLine(
        title=_('Attribution'),
        required=False)

    url = zope.schema.URI(
        title=_('URL'),
        required=False)

    text_2 = zope.schema.Text(
        title=_('Citation 2'),
        required=False)

    attribution_2 = zope.schema.TextLine(
        title=_('Attribution 2'),
        required=False)

    url_2 = zope.schema.URI(
        title=_('URL 2'),
        required=False)

    layout = zope.schema.Choice(
        title=_('Layout'),
        source=CitationLayoutSource(),
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


class IBreakingNewsBody(zope.interface.Interface):

    text = zope.schema.Text(
        title=_('Article body'),
        default=_('breaking-news-more-shortly'),
        required=False)

    article_id = zope.interface.Attribute(
        'The uniqueID of the breaking news article')
