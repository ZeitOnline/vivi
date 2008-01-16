# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent.mapping
import zope.interface

import zeit.connector.interfaces


class WebDAVProperties(persistent.mapping.PersistentMapping):

    zope.interface.implements(zeit.connector.interfaces.IWebDAVProperties)

    def __repr__(self):
        return object.__repr__(self)



class Resource(object):
    """Represents a resource in the webdav."""

    zope.interface.implements(zeit.connector.interfaces.IResource)

    def __init__(self, id, name, type, data, properties=None, contentType=''):
        self.id = id
        self.__name__ = name
        self.type = type
        self.data = data
        if properties is None:
            properties = {}
        self.properties = WebDAVProperties(properties)
        self.contentType = contentType



class CachedResource(object):
    """Represents a resource in the webdav."""

    zope.interface.implements(zeit.connector.interfaces.IResource)

    def __init__(self, id, name, type_name, property_getter, body_getter,
                 content_type):
        self.id = id
        self.__name__ = name
        self.type = type_name
        self._propterty_getter = property_getter
        self._body_getter = body_getter
        self.contentType = content_type

    @property
    def data(self):
        return self._body_getter()

    @property
    def properties(self):
        return WebDAVProperties(self._propterty_getter())
