# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.magazin.interfaces


class TemplateSettings(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.magazin.interfaces.IArticleTemplateSettings)

    zeit.cms.content.dav.mapProperties(
        zeit.magazin.interfaces.IArticleTemplateSettings,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('template', 'header_layout'))
