# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zeit.cms.content.property


class CommonMetadata(object):

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('year', 'volume', 'ressort', 'serie', 'copyrights',
         'page'))

    # tuple/set doesn't work with webdav, yet
    #zeit.cms.content.dav.mapProperty(
    #    zeit.cms.content.interfaces.ICommonMetadata['authors'],
    #    zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
    #    'author')

    authors = zeit.cms.content.property.MultipleAttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'author')

    title = zeit.cms.content.property.ObjectPathProperty(
        '.body.title')
    subtitle = zeit.cms.content.property.ObjectPathProperty(
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
