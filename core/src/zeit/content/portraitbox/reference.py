import zeit.cms.content.dav
import grokcore.component as grok
import zeit.cms.interfaces
import zeit.content.portraitbox.interfaces


@grok.implementer(zeit.content.portraitbox.interfaces.IPortraitboxReference)
class PortraitboxReference(zeit.cms.content.dav.DAVPropertiesAdapter):
    portraitbox = zeit.cms.content.dav.DAVProperty(
        zeit.content.portraitbox.interfaces.IPortraitboxReference['portraitbox'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'artbox_portrait',
    )
