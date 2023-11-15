import persistent.mapping
import zeit.connector.interfaces
import zope.interface


@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
class WebDAVProperties(persistent.mapping.PersistentMapping):
    def __repr__(self):
        return object.__repr__(self)


class ReadOnlyWebDAVProperties(WebDAVProperties):
    def __init__(self, adict=None):
        super().__init__()
        if adict is not None:
            self.data.update(adict)

    def __delitem__(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def __setitem__(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def clear(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def update(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def setdefault(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def pop(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')

    def popitem(self, *args, **kwargs):
        raise RuntimeError('Cannot write on ReadOnlyWebDAVProperties')


@zope.interface.implementer(zeit.connector.interfaces.IResource)
class Resource:
    """Represents a resource in the webdav."""

    def __init__(self, id, name, type, data, properties=None, contentType=''):
        self.id = id
        self.__name__ = name
        self.type = type
        self.data = data
        if properties is None:
            properties = {}
        self.properties = WebDAVProperties(properties)
        self.contentType = contentType


@zope.interface.implementer(zeit.connector.interfaces.IResource)
class CachedResource:
    """Represents a resource in the webdav."""

    def __init__(self, id, name, type_name, property_getter, body_getter, contentType):
        self.id = id
        self.__name__ = name
        self.type = type_name
        self._property_getter = property_getter
        self._body_getter = body_getter
        self.contentType = contentType

    @property
    def data(self):
        return self._body_getter()

    @property
    def properties(self):
        return ReadOnlyWebDAVProperties(self._property_getter())


class WriteableCachedResource(CachedResource):
    """Used by mock connector"""

    def __init__(self, id, name, type_name, property_getter, body_getter, contentType):
        super().__init__(id, name, type_name, property_getter, body_getter, contentType)
        self._properties = WebDAVProperties(self._property_getter())

    @property
    def properties(self):
        return self._properties
