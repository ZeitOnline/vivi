# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.keyword
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zope.browser.interfaces
import zope.component
import zope.interface
import zope.publisher.browser


class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.cms.content.interfaces.ICommonMetadata)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        (
            'banner',
            'banner_id',
            'breaking_news',
            'cap_title',
            'color_scheme',
            'copyrights',
            'countings',
            'foldable',
            'is_content',
            'minimal_header',
            'page',
            'ressort',
            'serie',
            'sub_ressort',
            'vg_wort_id',
            'volume',
            'year',
        ))

    authors = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['authors'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'author',
        use_default=True)

    author_references = zeit.cms.content.property.MultiResource(
        '.head.author', xml_reference_name='author')

    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['commentsAllowed'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comments')

    commentSectionEnable = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['commentSectionEnable'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comment_section')

    keywords = zeit.cms.content.keyword.KeywordsProperty()

    title = zeit.cms.content.property.Structure(
        '.body.title',
        zeit.cms.content.interfaces.ICommonMetadata['title'])
    subtitle = zeit.cms.content.property.Structure(
        '.body.subtitle',
        zeit.cms.content.interfaces.ICommonMetadata['subtitle'])
    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle',
        zeit.cms.content.interfaces.ICommonMetadata['supertitle'])
    byline = zeit.cms.content.property.ObjectPathProperty(
        '.body.byline',
        zeit.cms.content.interfaces.ICommonMetadata['byline'])

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.title',
        zeit.cms.content.interfaces.ICommonMetadata['teaserTitle'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.text',
        zeit.cms.content.interfaces.ICommonMetadata['teaserText'])

    printRessort = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['printRessort'],
        zeit.cms.interfaces.PRINT_NAMESPACE, 'ressort')

    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['dailyNewsletter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        'http://namespaces.zeit.de/CMS/workflow', 'product-id')
    _product_text = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        'http://namespaces.zeit.de/CMS/workflow', 'product-name')

    @property
    def product(self):
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value

    @product.setter
    def product(self, value):
        if value is not None:
            if self._product_id == value.id:
                return
            self._product_id = value.id
            self._product_text = value.title
        else:
            self._product_id = None
            self._product_text = None

    @property
    def product_text(self):
        return self._product_text
