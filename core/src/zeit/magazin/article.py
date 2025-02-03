import grokcore.component as grok

import zeit.cms.content.dav
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.magazin.interfaces


@grok.implementer(zeit.magazin.interfaces.IRelatedLayout)
class RelatedLayout(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.magazin.interfaces.IRelatedLayout,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('related_layout',),
    )
