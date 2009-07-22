# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zope.component.interfaces
import zope.file.interfaces
import zope.interface
import zope.lifecycleevent


class IBeforeObjectAddEvent(zope.component.interfaces.IObjectEvent):
    """An event sent before an object will be added to the repository."""


class BeforeObjectAddEvent(zope.component.interfaces.ObjectEvent):
    """An event sent before an object will be added to the repository."""

    zope.interface.implements(IBeforeObjectAddEvent)


class IAfterObjectConstructedEvent(zope.component.interfaces.IObjectEvent):
    """An event sent after an ICMSContent is constructed from a resource."""

    resource = zope.interface.Attribute(
        'IResource the object was constructed from')


class AfterObjectConstructedEvent(zope.component.interfaces.ObjectEvent):
    """An event sent after an ICMSContent is constructed from a resource."""

    zope.interface.implements(IAfterObjectConstructedEvent)

    def __init__(self, obj, resource):
        self.object = obj
        self.resource = resource


class IBeforeObjectRemovedEvent(zope.lifecycleevent.IObjectRemovedEvent):
    """An event sent after an ICMSContent is removed from a resource."""


class BeforeObjectRemovedEvent(zope.lifecycleevent.ObjectRemovedEvent):
    """An event sent after an ICMSContent is removed from a resource."""

    zope.interface.implements(IBeforeObjectRemovedEvent)


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

        raises TypeError if unique_id is not a basestring.
        raises ValueError if the unique_id is invalid (i.e. does not start with
            the correct prefix).
        raises KeyError if unique_id is not referencing a valid object.

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

        An IBeforeObjectAddEvent is sent before the object is added to the
        repository.

        """


class IUnknownResource(zeit.cms.interfaces.ICMSContent):
    """Unknown resource content.

    When an object in the repository cannot be identified or there is no way to
    create a suitable ICMSContent an object implementing IUnknownResource
    may be used.

    """

    type = zope.interface.Attribute("Raw type info got from connector.")


class IFile(zeit.cms.interfaces.ICMSContent,
            zope.file.interfaces.IFile):
    """A file like object in the CMS."""


class ICollection(zope.app.container.interfaces.IContainer):
    """A collection."""


class IFolder(ICollection, zeit.cms.interfaces.ICMSContent):
    """A normal folder in the cms."""


class IRepositoryContent(zope.interface.Interface):
    """Marker interface for content in the repository."""


class IUserPreferences(zope.interface.Interface):
    """User preferences regarding the repository."""

    def hide_container(container):
        """Mark the container as hidden."""

    def show_container(container):
        """Mark the container as shown."""

    def is_hidden(container):
        """Return if the container is hidden."""

    def get_hidden_containers():
        """Returen a set of hidden containers."""
