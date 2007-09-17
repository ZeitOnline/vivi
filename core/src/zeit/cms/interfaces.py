# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.i18nmessageid
import zope.interface
import zope.schema

import zope.app.container.interfaces

import zc.form.field


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


DOCUMENT_SCHEMA_NS = u"http://namespaces.zeit.de/CMS/document"
ID_NAMESPACE = u'http://xml.zeit.de/'
TEASER_NAMESPACE = u'http://xml.zeit.de/CMS/Teaser'
DeleteProperty = object()  # marker for deleting properties in the dav


class LockingError(Exception):
    """Raised when trying to lock an already locked resource."""


class IConnector(zope.interface.Interface):
    """Connects the cms to the backend.

    This utility interfaces the CMSConnector provided by Thomas, Ralf, etc.

    """

    def listCollection(id):
        """List the contents of collection.

        id: unique id of the colleciton to list

        returns sequence of (local_id, unique_id). The unique ids normally
        have a form like
        `http://xml.zeit.de/(online)?/[Jahr]/[Ausgabe]/[Artikelname]` but
        callers should *not* rely on that.

        raises ValueError if the id is not valid or does not match the
         repository.
        raises KeyError if the resource does not exist.

        XXX define more error cases
        """


    def __getitem__(id):
        """Return the resource identified by `id`.

        returns an IResource instance.

        raises KeyError if the resource could not be found.

        """

    def __delitem__(id):
        """Remove the resource from the repository.

        raises KeyError if the resource could not be found.

        """

    def __setitem__(id, object):
        """Add the given `object` to the document store under the given name.

        The object must be adaptable to IResource.

        """

    def add(object):
        """Add the given `object` to the document store.

        The object must be adaptable to IResource.

        """

    def changeProperties(id, properties):
        """Change webdav properties of object.

        id: unique id
        properties: see IWebDAVProperties.properties

        """

    def lock(id, principal, until):
        """Lock resource for principal until a given datetime.

        id: unique id
        until: datetime until the lock is valid.

        """

    def unlock(id):
        """Unlock resource."""

    def locked(id):
        """Return whether a resource is locked or not.

        returns tuple <lock owner>, <locked until>, <my lock>
            lock owner: principal id
            locked until: datetime.datetime instance
            my lock: True if the lock was issued by this system, False
                otherwise.

        returns None, None if the resource is not locked.
        raises KeyError if the resource does not exist.

        """


class IWebDAVReadProperties(zope.interface.common.mapping.IEnumerableMapping):
    """Mapping for WebDAV properties.

    Keys are in the form (name, namespace), for example:

        {(u'resourcetype', u'DAV:'): u'article'}

    name, namespace and value should be unicode. If any is a str it must not
    contain non usascii characters.

    value can be the special value of DeleteProperty to indicate the property
    should be removed.

    """

class IWebDAVWriteProperties(zope.interface.common.mapping.IWriteMapping):
    """Write interface for WebDAVProperties."""


class IWebDAVProperties(IWebDAVReadProperties, IWebDAVWriteProperties):
    """Combined read and write interface for webdav properties."""


class IResource(zope.interface.Interface):
    """Represents a resource in the webdav.

    This is the resource interface the connector uses to return or get
    resources.
    """

    __name__ = zope.schema.TextLine(
        title=u"The name within the parent",
        description=u"Traverse the parent with this name to get the object.")

    # TODO: make this an URI. We want the unique ids to not contain any unicode
    # characters, so a URI would be the right thing. Right now we have unicode
    # unique ids though makeing URI invalid.
    id = zope.interface.Attribute("Unique id of resource")

    # TODO: make type a choice. This requires a source for valid types. We
    # might want to use the interface dotted name instead of just 'article' or
    # 'image'.
    type = zope.interface.Attribute("Resource type (folder, image, ...).")

    data = zope.interface.Attribute(
        u"Resource main data (body, image data) as a file-like object.")
    contentType = zope.schema.BytesLine(
        title=u"Content Type",
        description=u'The mime content type identifies the type of data.',
        default='',
        required=False)

    properties = zope.schema.Object(
        IWebDAVProperties,
        title=u"WebDAV properties")


class ICMSContent(zope.interface.Interface):
    """Interface for all CMS content being loaded from the repository.

    """

    uniqueId = zope.schema.TextLine(
        title=_("Unique Id"),
        readonly=True)

    __name__ = zope.schema.TextLine(
        title=_("File name"))
