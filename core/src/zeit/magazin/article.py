import grokcore.component as grok
import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.magazin.interfaces


@zope.interface.implementer(zeit.magazin.interfaces.INextRead)
class NextRead(zeit.cms.related.related.RelatedBase):
    nextread = zeit.cms.content.reference.MultiResource('.head.nextread.reference', 'related')


@grok.implementer(zeit.magazin.interfaces.IRelatedLayout)
class RelatedLayout(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.magazin.interfaces.IRelatedLayout,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('related_layout', 'nextread_layout'),
    )
