from io import StringIO
from zeit.cms.content.cache import writeabledict
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
import gocept.cache.property
import grokcore.component as grok
import hashlib
import json
import lxml.etree
import lxml.objectify
import re
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.cms.workflow.interfaces
import zeit.connector.filesystem
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.edit.interfaces
import zeit.edit.rule
import zeit.workflow.interfaces
import zeit.workflow.workflow
import zope.component
import zope.dublincore.interfaces
import zope.index.text.interfaces
import zope.interface
import zope.security.proxy

ARTICLE_NS = zeit.content.article.interfaces.ARTICLE_NS
# supertitle+title+subtitle are here since their order is important for XSLT,
# and the XML-properties will reuse existing nodes, so the order will be as we
# want it.
ARTICLE_TEMPLATE = """\
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head>
        <header/>
    </head>
    <body>
        <supertitle/>
        <title/>
        <subtitle/>
    </body>
</article>"""


class ToggleableAccess(zeit.cms.content.dav.DAVProperty):

    def __get__(self, instance, class_, properties=None):
        value = super().__get__(instance, class_, properties)
        if FEATURE_TOGGLES.find(
                'access_treat_free_as_dynamic') and value == 'free':
            return 'dynamic'
        return value


@zope.interface.implementer(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.interfaces.IEditorialContent)
class Article(zeit.cms.content.metadata.CommonMetadata):
    """Article is the main content type in the Zeit CMS."""

    default_template = ARTICLE_TEMPLATE

    cache = gocept.cache.property.TransactionBoundCache(
        '_v_article_cache', writeabledict)

    textLength = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['textLength'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'text-length')

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'artbox_thema', 'audio_speechbert', 'genre',
         'template', 'header_layout', 'header_color',
         'hide_ligatus_recommendations', 'prevent_ligatus_indexing',
         'comments_sorting'))

    access = ToggleableAccess(
        ICommonMetadata['access'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'access', use_default=True)

    has_audio = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['has_audio'],
        zeit.cms.interfaces.PRINT_NAMESPACE, 'has_audio', use_default=True)

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(self)

    @property
    def header(self):
        return zeit.content.article.edit.interfaces.IHeaderArea(self)

    @property
    def paragraphs(self):
        return len(self.xml.xpath('//body/division/p'))

    def updateDAVFromXML(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self)
        modified = []
        for (name, ns), value in zeit.connector.filesystem.parse_properties(
                self.xml).items():
            if not value:
                continue
            properties[(name, ns)] = value
            prop = zeit.cms.content.dav.findProperty(
                zeit.cms.content.metadata.CommonMetadata, name, ns)
            if prop:
                modified.append(prop.field.__name__)
        zope.lifecycleevent.modified(
            self, zope.lifecycleevent.Attributes(
                zeit.cms.content.interfaces.ICommonMetadata, *modified))

    @property
    def main_image_block(self):
        try:
            image_block = self.body.values()[0]
        except IndexError:
            return None
        if not zeit.content.article.edit.interfaces.IImage.providedBy(
                image_block):
            return None
        return image_block

    @property
    def main_image(self):
        image_block = self.main_image_block
        if image_block is None:
            # XXX Duplicates configuration from .edit.image.Image.
            # XXX Kludgy: We're passing the article as the source here, but
            # that will be replaced by having the article create the image
            # block and then use *that* as the source, so it all works out.
            return NoMainImageBlockReference(self, 'references', 'image')
        return image_block.references

    @main_image.setter
    def main_image(self, value):
        image_block = self.main_image_block
        if image_block is None:
            image_block = self._create_image_block_in_front()
        image_block.references = value

    @property
    def main_image_variant_name(self):
        image_block = self.main_image_block
        if image_block is None:
            return None
        return image_block.variant_name

    @main_image_variant_name.setter
    def main_image_variant_name(self, value):
        image_block = self.main_image_block
        if image_block is None:
            return
        image_block.variant_name = value

    def _create_image_block_in_front(self):
        body = self.body
        image_block = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'image')()
        ids = body.keys()
        ids.insert(0, ids.pop())  # XXX ElementFactory should do this
        body.updateOrder(ids)
        return image_block


class NoMainImageBlockReference(zeit.cms.content.reference.EmptyReference):
    """We need someone who can create references, even when the reference is
    empty. In case of the main image, not only can the reference be empty,
    the block containing the reference might not even exist. So we need a
    proxy who creates the block if necessary.

    XXX The whole main_image thing is a kludge, and it shows here.
    """

    def create(self, target):
        self.source = self.source._create_image_block_in_front()
        return super().create(target)


class ArticleType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Article
    interface = zeit.content.article.interfaces.IArticle
    type = 'article'
    title = _('Article')


@zope.interface.implementer(zeit.content.article.interfaces.IArticle)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def articleFromTemplate(context):
    source = StringIO(zeit.cms.content.interfaces.IXMLSource(context))
    article = Article(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context))
    return article


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def updateTextLengthOnChange(object, event):
    length = zope.security.proxy.removeSecurityProxy(object.xml).body.xpath(
        'string-length()')
    try:
        object.textLength = int(length)
    except zope.security.interfaces.Unauthorized:
        # Ignore when we're not allowed to set it.
        pass


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def disallowCommentsIfCommentsAreNotShown(object, event):
    if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(object):
        return
    if not object.commentSectionEnable:
        object.commentsAllowed = False


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def modify_speechbert_audio_depeding_on_genre(article, event):
    """Checkbox speechbert audio depends on article-genres.xml"""
    genres = zeit.content.article.interfaces.IArticle['genre'].source(None)
    for desc in event.descriptions:
        if (desc.interface is zeit.content.article.interfaces.IArticle and
                'genre' in desc.attributes):
            if (genres.audio(article.genre) == 'speechbert' or
                    not article.genre):
                article.audio_speechbert = True
            else:
                article.audio_speechbert = False


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def iter_referenced_content(context):
    referenced_content = []
    body = context.body
    if not body:
        return referenced_content
    for element in body.values():
        if zeit.content.article.edit.interfaces.IReference.providedBy(
                element) and element.references:
            if zeit.cms.content.interfaces.IReference.providedBy(
                    element.references):
                if element.references.target:
                    referenced_content.append(element.references.target)
            else:
                referenced_content.append(element.references)
    return referenced_content


@grok.implementer(zope.index.text.interfaces.ISearchableText)
class SearchableText(grok.Adapter):
    """SearchableText for an article."""

    grok.context(zeit.content.article.interfaces.IArticle)

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.body.xpath("//p//text()"):
            text = str(p).strip()
            if text:
                main_text.append(text)
        return main_text


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
class ArticleWorkflow(zeit.workflow.workflow.ContentWorkflow):

    def can_publish(self):
        result = super().can_publish()
        if result == CAN_PUBLISH_ERROR:
            return CAN_PUBLISH_ERROR
        validator = zeit.edit.rule.ValidatingWorkflow(self.context)
        result = validator.can_publish()
        self.error_messages = validator.error_messages
        return result


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.cms.workflow.interfaces.IPublishPriority)
def publish_priority_article(context):
    # Since breaking news should be published faster articles, we give them
    # the same priority as the homepage
    if zeit.content.article.interfaces.IBreakingNews(context).is_breaking:
        return zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE
    return zeit.cms.workflow.interfaces.PRIORITY_HIGH


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def ensure_division_handler(context, event):
    context.body.ensure_division()


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def set_default_values(context, event):
    zeit.cms.content.field.apply_default_values(
        context, zeit.content.article.interfaces.IArticle)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def set_template_and_header_defaults(context, event):
    source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE(context)

    if ((not context.template and not context.header_layout) or
            context.template not in source):
        template, header_layout = source.factory.get_default_template(context)

        context.template = template if template else None
        context.header_layout = header_layout if header_layout else None

    source = zeit.content.article.source.MAIN_IMAGE_VARIANT_NAME_SOURCE
    if (context.main_image_block and
            context.main_image_block._variant_name not in source(context) and
            (context.template or context.header_layout)):
        context.main_image_variant_name = source.factory.get_default(context)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def set_default_header_when_template_is_changed(context, event):
    for desc in event.descriptions:
        if (desc.interface is zeit.content.article.interfaces.IArticle and
                'template' in desc.attributes):
            break
    else:
        return

    source = zeit.content.article.source.ARTICLE_TEMPLATE_SOURCE(context)
    header_layout = source.factory.get_default_header(context)
    context.header_layout = header_layout if header_layout else None


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def ensure_block_ids(context, event):
    body = context.body
    # Keys are generated on demand, so we force this once, otherwise a
    # consistent result is not guaranteed (since different requests might
    # overlap and thus generate different keys).
    body.keys()
    body.ensure_division()


_QUOTE_CHARACTERS = r'[\u201c\u201d\u201e\u201f\u00ab\u00bb]'
QUOTE_CHARACTERS = re.compile(_QUOTE_CHARACTERS)
QUOTE_CHARACTERS_OPEN = re.compile(rf'{_QUOTE_CHARACTERS}(\w)')
QUOTE_CHARACTERS_CLOSE = re.compile(rf'([\w\.]){_QUOTE_CHARACTERS}')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def normalize_quotation_marks(context, event):
    # XXX objectify has immutable text/tail. le sigh.
    normalize = normalize_quotes if FEATURE_TOGGLES.find(
        'normalize_quotes') else normalize_quotes_to_inch_sign
    context.xml.body = lxml.objectify.fromstring(lxml.etree.tostring(
        normalize(
            lxml.etree.fromstring(lxml.etree.tostring(context.xml.body)))))

    if context.xml.find('teaser') is not None:
        context.xml.teaser = lxml.objectify.fromstring(lxml.etree.tostring(
            normalize(
                lxml.etree.fromstring(
                    lxml.etree.tostring(context.xml.teaser)))))


def normalize_quotes(node):
    if node.text:
        node.text = QUOTE_CHARACTERS_OPEN.sub(r'»\1', node.text)
        node.text = QUOTE_CHARACTERS_CLOSE.sub(r'\1«', node.text)
    if node.tail:
        node.tail = QUOTE_CHARACTERS_OPEN.sub(r'»\1', node.tail)
        node.tail = QUOTE_CHARACTERS_CLOSE.sub(r'\1«', node.tail)
    for child in node.iterchildren():
        normalize_quotes(child)
    return node


def normalize_quotes_to_inch_sign(node):
    if node.text:
        node.text = QUOTE_CHARACTERS.sub('"', node.text)
    if node.tail:
        node.tail = QUOTE_CHARACTERS.sub('"', node.tail)
    for child in node.iterchildren():
        normalize_quotes_to_inch_sign(child)
    return node


class ArticleMetadataUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.content.article.interfaces.IArticle

    def update_with_context(self, node, context):
        if context.genre:
            node.set('genre', context.genre)


@zope.interface.implementer(
    zeit.content.article.interfaces.ISpeechbertChecksum)
class Speechbert(zeit.cms.content.dav.DAVPropertiesAdapter):

    checksum = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.ISpeechbertChecksum['checksum'],
        zeit.cms.interfaces.SPEECHBERT_NAMESPACE, 'checksum',
        writeable=zeit.cms.content.interfaces.WRITEABLE_LIVE)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def calculate_checksum(context, event):
    speechbert = zope.component.getAdapter(
        context, zeit.workflow.interfaces.IPublisherData, name='speechbert')
    if speechbert.ignore('publish'):
        return
    checksum = hashlib.md5(usedforsecurity=False)
    body = json.dumps(speechbert.get_body(), ensure_ascii=False).encode(
        'utf-8')
    checksum.update(body)
    article = zeit.content.article.interfaces.ISpeechbertChecksum(context)
    article.checksum = checksum.hexdigest()
