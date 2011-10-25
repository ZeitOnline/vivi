# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import StringIO
import grokcore.component
import lxml.etree
import lxml.objectify
import zeit.cms.checkout.interfaces
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.rule
import zeit.workflow.dependency
import zeit.workflow.interfaces
import zeit.wysiwyg.html
import zeit.wysiwyg.interfaces
import zope.app.container.contained
import zope.component
import zope.dublincore.interfaces
import zope.index.text.interfaces
import zope.interface
import zope.security.proxy


ARTICLE_NS = zeit.content.article.interfaces.ARTICLE_NS
ARTICLE_TEMPLATE = """\
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
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
        ('has_recensions', 'artbox_thema', 'layout'))

    @property
    def paragraphs(self):
        return len(self.xml.xpath('//body/division/p'))

    def updateDAVFromXML(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self)
        for el in self.xml.head.attribute:
            name = el.get('name')
            ns = el.get('ns')
            value = el.text
            if value:
                properties[(name, ns)] = value


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


class ArticleHTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    """HTML content of an article."""

    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    def get_tree(self):
        return self.context.xml['body']


class PageBreakStep(zeit.wysiwyg.html.ConversionStep):

    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    weight = -3
    xpath_xml = '.'
    xpath_html = '.'

    DEFAULT_DIVISONS_PER_PAGE = 7

    def to_html(self, root):
        # pull up children behind their divisions
        for division in root.xpath('division[@type="page"]'):
            for i, child in enumerate(division.iterchildren()):
                root.insert(root.index(division) + 1 + i, child)

        # page-breaks shall be only *between* pages, so the first one
        # is superfluous
        divisions = root.xpath('division[@type="page"]')
        if divisions:
            root.remove(divisions[0])

    def to_xml(self, root):
        if root.xpath('division[@type="page"]'):
            # one division must always exist
            division = lxml.etree.Element('division', **{'type': 'page'})
            root.insert(0, division)

            for node in root.iterchildren():
                if node.tag == 'division' and node.get('type') == 'page':
                    division = node
                else:
                    division.append(node)
        else:
            # one division must always exist
            i = self.DEFAULT_DIVISONS_PER_PAGE + 1
            for node in root.iterchildren():
                if i > self.DEFAULT_DIVISONS_PER_PAGE:
                    division = lxml.etree.Element(
                        'division', **{'type': 'page'})
                    root.insert(root.index(node), division)
                    i = 1

                division.append(node)
                if node.tag == 'p':
                    i += 1


class DivisionStep(zeit.wysiwyg.html.ConversionStep):

    # XXX structurally similar to zeit.wysiwyg.html.RawXMLStep

    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    xpath_xml = './/division[@type="page"]'
    xpath_html = './/*[contains(@class, "page-break")]'

    def to_html(self, node):
        teaser = node.get('teaser', '')
        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(teaser, **{'class': 'teaser'}),
            **{'class': 'inline-element page-break'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        match = node.xpath('div[@class="teaser"]')
        teaser = unicode(match[0]) if match else ''
        new_node = lxml.etree.Element('division', **{'type': 'page',
                                                     'teaser': teaser})
        return new_node


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


class SearchableText(grokcore.component.Adapter):
    """SearchableText for an article."""

    grokcore.component.context(zeit.content.article.interfaces.IArticle)
    grokcore.component.implements(zope.index.text.interfaces.ISearchableText)

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.body.xpath("//p//text()"):
            text = unicode(p).strip()
            if text:
                main_text.append(text)
        return main_text


class ValidatingContentWorkflow(zeit.edit.rule.ValidatingWorkflow):

    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    def can_publish(self):
        cwf = zeit.workflow.interfaces.IContentWorkflow(self.context)
        if not cwf.can_publish():
            return False
        return super(ValidatingContentWorkflow, self).can_publish()


@grokcore.component.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def ensure_division_handler(context, event):
    body = zeit.content.article.edit.interfaces.IEditableBody(context)
    body.ensure_division()
