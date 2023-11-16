import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces


@zope.interface.implementer(zeit.cms.content.interfaces.IRemoteMetadata)
class RemoteMetadata(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.IRemoteMetadata,
        zeit.cms.interfaces.ZEITWEB_NAMESPACE,
        ('remote_image', 'remote_timestamp'),
    )
