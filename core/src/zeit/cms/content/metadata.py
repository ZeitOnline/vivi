# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.keyword
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.syndication.interfaces


class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('serie', 'copyrights', 'year', 'volume', 'ressort', 'page',
         'sub_ressort', 'vg_wort_id'))

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

    shortTeaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.indexteaser.title')
    shortTeaserText = zeit.cms.content.property.ObjectPathProperty(
        '.indexteaser.text')

    hpTeaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.homepageteaser.title')
    hpTeaserText = zeit.cms.content.property.ObjectPathProperty(
        '.homepageteaser.text')

    automaticMetadataUpdateDisabled = zeit.cms.content.dav.DAVProperty(
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate[
            'automaticMetadataUpdateDisabled'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'automaticMetadataUpdateDisabled',
        use_default=True)

    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['dailyNewsletter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')
