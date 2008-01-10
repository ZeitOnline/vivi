# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import copy
import htmlentitydefs
import StringIO

import lxml.etree
import gocept.lxml.objectify

import persistent
import rwproperty

import zope.component
import zope.interface
import zope.security.proxy

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.wysiwyg.interfaces

import zeit.content.article.interfaces
import zeit.content.article.syndication


ARTICLE_NS = zeit.content.article.interfaces.ARTICLE_NS
ARTICLE_TEMPLATE = """\
<article>
    <head/>
    <body/>
</article>"""


class ImageProperty(object):

    def __get__(self, instance, class_):
        if instance is None:
            return class_
        images = []
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for image_element in self.image_elements(instance):
            unique_id = image_element.get('base-id')
            if unique_id is None:
                unique_id = image_element.get('src')
            try:
                content = repository.getContent(unique_id)
            except (ValueError, KeyError):
                continue
            images.append(content)
        return tuple(images)

    def __set__(self, instance, values):
        for element in self.image_elements(instance):
            element.getparent().remove(element)
        if not values:
            return
        for image in values:
            image_element = instance.xml.makeelement('image')

            # XXX this is quite hairy; shouldn't we use adapters?
            if zeit.content.image.interfaces.IImage.providedBy(image):
                image_element.set('src', image.uniqueId)
                image_element.set('type', image.contentType.split('/')[-1])
            elif zeit.content.image.interfaces.IImageGroup.providedBy(image):
                image_element.set('base-id', image.uniqueId)
            else:
                raise ValueError("%r is not an image." % image)

            image_metadata = zeit.content.image.interfaces.IImageMetadata(
                image)
            expires = image_metadata.expires
            if expires:
                expires = expires.isoformat()
                image_element.set('expires', expires)
            image_element.bu = image_metadata.caption or ''
            image_element.copyright = image_metadata.copyrights
            instance.xml.head.append(image_element)

    def image_elements(self, instance):
        return instance.xml.head.findall('image')


class Article(zeit.cms.content.metadata.CommonMetadata):
    """Article is the main content type in the Zeit CMS."""

    zope.interface.implements(
        zeit.content.article.interfaces.IArticle,
        zeit.wysiwyg.interfaces.IHTMLContent)

    default_template = ARTICLE_TEMPLATE

    textLength = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'text-length')

    commentsAllowed = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comments')
    banner = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'banner')
    boxMostRead = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'mostread')
    pageBreak = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'paragraphsperpage')
    dailyNewsletter = zeit.cms.content.property.AttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')

    syndicatedIn = zeit.cms.content.property.ResourceSet(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'syndicatedIn')
    automaticTeaserSyndication = zeit.cms.content.property.ResourceSet(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'automaticTeaserSyndication')
    syndicationLog = zeit.content.article.syndication.SyndicationLogProperty()

    images = ImageProperty()

    navigation = zeit.cms.content.dav.DAVProperty(
        zeit.content.article.interfaces.IArticle['navigation'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'ressort')

    @rwproperty.getproperty
    def html(self):
        """return html snippet of article."""
        html = []
        for node in self._html_getnodes():
            if node.tag == 'intertitle':
                node = copy.copy(node)
                node.tag = 'h3'
            html.append(lxml.etree.tounicode(node, pretty_print=True))
        return '\n'.join(html)


    @rwproperty.setproperty
    def html(self, value):
        """set article html."""
        value = '<div>' + self._replace_entities(value) + '</div>'
        html = gocept.lxml.objectify.fromstring(value)
        for node in self._html_getnodes():
            parent = node.getparent()
            parent.remove(node)
        body = self.xml.body
        for node in html.iterchildren():
            if node.tag == 'h3':
                node.tag = 'intertitle'
            body.append(node)

    def _html_getnodes(self):
        for node in self.xml.body.iterchildren():
            if node.tag in ('p', 'intertitle'):
                yield node

    @staticmethod
    def _replace_entities(value):
        for entity_name, codepoint in htmlentitydefs.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&'+entity_name+';', unichr(codepoint))
        return value


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def articleFactory(context):
    article = Article(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVWriteProperties(article).update(
        context.properties)
    return article


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
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def mapPropertyToAttribute(article, event):
    attribute = zeit.cms.content.property.AttributeProperty(
        event.property_namespace, event.property_name)
    attribute.__set__(article, event.new_value)


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
