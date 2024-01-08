import grokcore.component as grok

import zeit.cms.content.dav
import zeit.content.infobox.interfaces


@grok.implementer(zeit.content.infobox.interfaces.IInfoboxReference)
class InfoboxReference(zeit.cms.content.dav.DAVPropertiesAdapter):
    infobox = zeit.cms.content.dav.DAVProperty(
        zeit.content.infobox.interfaces.IInfoboxReference['infobox'],
        'http://namespaces.zeit.de/CMS/document',
        'artbox_info',
    )
