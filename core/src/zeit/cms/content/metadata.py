# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import rwproperty
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.keyword
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.syndication.interfaces
import zope.browser.interfaces
import zope.component
import zope.interface
import zope.publisher.browser


class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        (
            'banner',
            'banner_id',
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
            'sub_type',
            'vg_wort_id',
            'volume',
            'year',
        ))

    authors = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['authors'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'author',
        use_default=True)

    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['commentsAllowed'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comments')

    keywords = zeit.cms.content.keyword.KeywordsProperty()

    title = zeit.cms.content.property.Structure(
        '.body.title')
    subtitle = zeit.cms.content.property.Structure(
        '.body.subtitle')
    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle')
    byline = zeit.cms.content.property.ObjectPathProperty(
        '.body.byline')

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.title')
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.text')

    automaticMetadataUpdateDisabled = zeit.cms.content.dav.DAVProperty(
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate[
            'automaticMetadataUpdateDisabled'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'automaticMetadataUpdateDisabled',
        use_default=True)

    printRessort = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['printRessort'],
        zeit.cms.interfaces.PRINT_NAMESPACE, 'ressort')

    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['dailyNewsletter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')

    _product_id = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['product_id'],
        'http://namespaces.zeit.de/CMS/workflow', 'product-id')
    _product_text = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        'http://namespaces.zeit.de/CMS/workflow', 'product-name')

    @rwproperty.getproperty
    def product_id(self):
        return self._product_id


    @rwproperty.setproperty
    def product_id(self, value):
        if self._product_id == value:
            return
        self._product_id = value
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'product_id'].source(self)
        # Set title        
        request = zope.publisher.browser.TestRequest()
        terms = zope.component.getMultiAdapter(
            (source, request), zope.browser.interfaces.ITerms)
        self._product_text = terms.getTerm(value).title

    @property
    def product_text(self):
        return self._product_text

