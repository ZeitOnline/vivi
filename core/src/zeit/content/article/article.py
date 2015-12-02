from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import CAN_PUBLISH_SUCCESS
from zeit.cms.workflow.interfaces import CAN_PUBLISH_WARNING
from zope.cachedescriptors.property import Lazy as cachedproperty
import StringIO
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import re
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
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
    <head/>
    <body>
        <supertitle/>
        <title/>
        <subtitle/>
    </body>
</article>"""


class Article(zeit.cms.content.metadata.CommonMetadata):
    """Article is the main content type in the Zeit CMS."""

    zope.interface.implements(zeit.content.article.interfaces.IArticle,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = ARTICLE_TEMPLATE

    textLength = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['textLength'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'text-length')

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'artbox_thema', 'layout', 'genre',
         'template', 'header_layout', 'is_instant_article', 'is_amp'))

    @property
    def paragraphs(self):
        return len(self.xml.xpath('//body/division/p'))

    def updateDAVFromXML(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self)
        modified = []
        for el in self.xml.head.attribute:
            name = el.get('name')
            ns = el.get('ns')
            value = el.text
            if value:
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
        body = zeit.content.article.edit.interfaces.IEditableBody(self)
        try:
            image_block = body.values()[0]
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
    def main_image_layout(self):
        image_block = self.main_image_block
        if image_block is None:
            return None
        return image_block.layout

    @main_image_layout.setter
    def main_image_layout(self, value):
        image_block = self.main_image_block
        image_block.layout = value

    def _create_image_block_in_front(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self)
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
        return super(NoMainImageBlockReference, self).create(target)


class ArticleType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Article
    interface = zeit.content.article.interfaces.IArticle
    type = 'article'
    title = _('Article')


@zope.interface.implementer(zeit.content.article.interfaces.IArticle)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def articleFromTemplate(context):
    source = StringIO.StringIO(
        zeit.cms.content.interfaces.IXMLSource(context))
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


class LayoutDependency(object):

    zope.component.adapts(zeit.content.article.interfaces.IArticle)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        layout = self.context.layout
        if layout and self.needs_publishing(layout):
            return [layout]
        else:
            return []

    def needs_publishing(self, content):
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        dc = zope.dublincore.interfaces.IDCTimes(content)

        if not workflow.published:
            return True
        if not all((workflow.date_last_published, dc.modified)):
            return False

        return workflow.date_last_published < dc.modified


class SearchableText(grok.Adapter):
    """SearchableText for an article."""

    grok.context(zeit.content.article.interfaces.IArticle)
    grok.implements(zope.index.text.interfaces.ISearchableText)

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.body.xpath("//p//text()"):
            text = unicode(p).strip()
            if text:
                main_text.append(text)
        return main_text


class ArticleWorkflow(zeit.workflow.workflow.ContentWorkflow):

    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    def can_publish(self):
        result = super(ArticleWorkflow, self).can_publish()
        if result == CAN_PUBLISH_ERROR:
            return CAN_PUBLISH_ERROR
        validator = zeit.edit.rule.ValidatingWorkflow(self.context)
        result = validator.can_publish()
        self.error_messages = validator.error_messages
        return result


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def ensure_division_handler(context, event):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    body.ensure_division()


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def set_default_values(context, event):
    zeit.cms.browser.form.apply_default_values(
        context, zeit.content.article.interfaces.IArticle)


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def ensure_block_ids(context, event):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    # Keys are generated on demand, so we force this once, otherwise a
    # consistent result is not guaranteed (since different requests might
    # overlap and thus generate different keys).
    body.keys()
    body.ensure_division()


DOUBLE_QUOTE_CHARACTERS = re.compile(u'[\u201c\u201d\u201e\u201f\u00ab\u00bb]')


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def normalize_quotation_marks(context, event):
    # XXX objectify has immutable text/tail. le sigh.
    context.xml.body = lxml.objectify.fromstring(lxml.etree.tostring(
        normalize_quotes(
            lxml.etree.fromstring(lxml.etree.tostring(context.xml.body)))))


def normalize_quotes(node):
    if node.text:
        node.text = DOUBLE_QUOTE_CHARACTERS.sub(u'"', node.text)
    if node.tail:
        node.tail = DOUBLE_QUOTE_CHARACTERS.sub(u'"', node.tail)
    for child in node.iterchildren():
        normalize_quotes(child)
    return node


class ArticleMetadataUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.content.article.interfaces.IArticle

    def update_with_context(self, node, context):
        if context.genre:
            node.set('genre', context.genre)
