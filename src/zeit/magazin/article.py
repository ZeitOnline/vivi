# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.magazin.interfaces
import zope.interface


class TemplateSettings(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.magazin.interfaces.IArticleTemplateSettings)

    zeit.cms.content.dav.mapProperties(
        zeit.magazin.interfaces.IArticleTemplateSettings,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('template', 'header_layout'))


class NextRead(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.magazin.interfaces.INextRead)

    nextread = zeit.cms.content.reference.MultiResource(
        '.head.nextread.reference', 'related')


class RelatedLayout(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.magazin.interfaces.IRelatedLayout)

    zeit.cms.content.dav.mapProperties(
        zeit.magazin.interfaces.IRelatedLayout,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('related_layout', 'nextread_layout'))
