# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import StringIO
import datetime
import persistent
import zeit.cms.connector
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.type
import zope.app.container.contained
import zope.component
import zope.interface


class UnknownResource(zope.app.container.contained.Contained):
    """Represent an unknown resource"""

    zope.interface.implements(zeit.cms.repository.interfaces.IUnknownResource,
                              zeit.cms.content.interfaces.ITextContent)

    uniqueId = None

    def __init__(self, data, type_info=None):
        if not isinstance(data, unicode):
            raise TypeError('data must be unicode.')
        self.data = data
        self.type = type_info


class PersistentUnknownResource(UnknownResource,
                                persistent.Persistent):
    """An unknown resource that is also persistent.

    We create a new class for this to be backward compatible. Just adding
    persistent.Persisten above will yield an error:

        TypeError: ('object.__new__(UnknownResource) is not safe,
            use persistent.Persistent.__new__()',
            <function _reconstructor at 0x1995f0>,
            (<class 'zeit.cms.repository.unknown.UnknownResource'>,
            <type 'object'>, None))

    """


class UnknownResourceType(zeit.cms.type.TypeDeclaration):

    type = 'unknown'
    title = _('Unknown Resource')
    interface = zeit.cms.repository.interfaces.IUnknownResource
    addform = zeit.cms.type.SKIP_ADD

    def content(self, resource):
        return PersistentUnknownResource(
            unicode(resource.data.read(), 'latin1'), resource.type)

    def resource_body(self, content):
        return StringIO.StringIO(content.data.encode('latin1'))
