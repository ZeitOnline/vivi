# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.interfaces


class IRepository(zope.interface.Interface):
    """Access the webdav repository.

    This is the general entry point for accessing file and directory listings.

    """

    def getUniqueId(content):
        """Return unique not-changeable id of given content object.

        raises KeyError if no id could be determined.

        """

    def getContent(unique_id):
        """Return content object identified by given unique_id.

        During one request every call to this function with the same unique_id
        will return the *same* content object.

        raises KeyError if unique_id is not referencing a valid object.
        raises ValueError if the unique_id is invalid (i.e. does not start with
            the correct prefix).

        """

    def getCopyOf(unique_id):
        """Return a copy of the object identified by `unique_id`."""

    def getUncontainedConent(unique_id):
        """Return content object identified by given unique_id.

        Returns content like `getContent` but doesn't setup the containment
        hierarchy.

        """

    def addContent(object):
        """Add content to the repository.

        Raises TypeError if `object` is not adaptable to IResource.
        Raises ValueError if `object` does not have a uniqueId assigned.

        """


class IUnknownResource(zeit.cms.content.interfaces.ITextContent):
    """Unknown resource content.

    When an object in the repository cannot be identified or there is no way to
    create a suitable ICMSContent an object implementing IUnknownResource
    may be used.

    """

    type = zope.interface.Attribute("Raw type info got from connector.")

    dav_resource_type = zope.interface.Attribute(
        "Resource type the dav propagated (DAV:resorucetype)")


class ICollection(zope.app.container.interfaces.IContainer):
    """A collection."""


class IFolder(ICollection, zeit.cms.interfaces.ICMSContent):
    """A normal folder in the cms."""


class IRepositoryContent(zope.interface.Interface):
    """Marker interface for content in the repository."""


class IUserPreferences(zope.interface.Interface):
    """User preferences regarding the repository."""

    hidden_containers = zope.schema.Tuple(
        title=u"Verteckte Ordner",
        description=u"Ordner, die nicht im Navigationsbaum angezeigt werden.",
        default=(),
        value_type=zope.schema.Object(ICollection))
