import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces


@zope.interface.implementer(
    zeit.cms.content.interfaces.IRemoteMetadata)
class RemoteMetadata(zeit.cms.content.dav.DAVPropertiesAdapter):

    remote_image = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IRemoteMetadata['remote_image'],
        zeit.cms.interfaces.ZEITWEB_NAMESPACE,
        'remote_image'
        )

    remote_timestamp = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.IRemoteMetadata['remote_timestamp'],
        zeit.cms.interfaces.ZEITWEB_NAMESPACE,
        'remote_timestamp'
        )
