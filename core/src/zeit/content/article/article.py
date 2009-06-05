# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import copy
import lxml.etree
import lxml.objectify
import persistent
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.wysiwyg.html
import zeit.wysiwyg.interfaces
import zope.app.container.contained
import zope.component
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
    boxMostRead = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['boxMostRead'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'mostread')
    pageBreak = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['pageBreak'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'paragraphsperpage')

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('has_recensions', 'banner', 'artbox_thema'))

    @property
    def paragraphs(self):
        return len(self.xml.body.findall('p'))

    def updateDAVFromXML(self):
        properties = zeit.connector.interfaces.IWebDAVProperties(self)
        for el in self.xml.head.attribute:
            name = el.get('name')
            ns = el.get('ns')
            value = el.text
            if value:
                properties[(name, ns)] = value

articleFactory = zeit.cms.content.adapter.xmlContentFactory(Article)


@zope.interface.implementer(zeit.content.article.interfaces.IArticle)
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
def articleFromTemplate(context):
    source = StringIO.StringIO(
        zeit.cms.content.interfaces.IXMLSource(context))
    article = Article(xml_source=source)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        zeit.cms.interfaces.IWebDAVReadProperties(context))
    return article


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'article')
resourceFactory = zope.component.adapter(
    zeit.content.article.interfaces.IArticle)(resourceFactory)


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

    weight = -1.1
    xpath_xml = '.'
    xpath_html = '.'

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
            per_page = (
                self.context.pageBreak
                or zeit.content.article.interfaces.IArticleMetadata[
                    'pageBreak'].default)
            # one division must always exist
            i = per_page + 1
            for node in root.iterchildren():
                if i > per_page:
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
    xpath_html = './/*[@class="page-break"]'

    def to_html(self, node):
        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(node.get('teaser'), **{'class': 'page-break-teaser'}),
            **{'class': 'page-break'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        match = node.xpath('div[@class="page-break-teaser"]')
        teaser = unicode(match[0]) if match else ''
        new_node = lxml.etree.Element('division', **{'type': 'page',
                                                     'teaser': teaser})
        return new_node
