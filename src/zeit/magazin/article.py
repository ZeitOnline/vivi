# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.dav
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

    path = lxml.objectify.ObjectPath('.head.nextread.reference')

    @property
    def nextread(self):
        return self._get_related()

    @nextread.setter
    def nextread(self, value):
        return self._set_related(value)
