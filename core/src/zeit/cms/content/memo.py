import zope.interface

from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces


@zope.interface.implementer(zeit.cms.content.interfaces.IMemo)
class Memo(zeit.cms.content.dav.DAVPropertiesAdapter):
    memo = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IMemo['memo'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'memo',
        writeable=WRITEABLE_ALWAYS,
    )
