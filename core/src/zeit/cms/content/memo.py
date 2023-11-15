from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.interface


@zope.interface.implementer(zeit.cms.content.interfaces.IMemo)
class Memo(zeit.cms.content.dav.DAVPropertiesAdapter):
    memo = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IMemo['memo'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'memo',
        writeable=WRITEABLE_ALWAYS,
    )


@grok.subscribe(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_private_token(event):
    if event.name == 'memo':
        event.veto()
