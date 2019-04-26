import zeit.cms.content.dav
import grokcore.component
import zeit.cms.interfaces
import zeit.content.portraitbox.interfaces


class PortraitboxReference(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(
        zeit.content.portraitbox.interfaces.IPortraitboxReference)

    portraitbox = zeit.cms.content.dav.DAVProperty(
        zeit.content.portraitbox.interfaces.IPortraitboxReference[
            'portraitbox'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'artbox_portrait')
