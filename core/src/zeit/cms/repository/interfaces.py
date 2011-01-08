# Copyright (c) 2007-2011 gocept gmbh & co. kg
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


class ConflictError(Exception):
    """Raised when adding to the repository yields a conflict."""

    def __init__(self, uniqueId, *args):
        self.uniqueId = uniqueId
        self.args = args


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

    def addContent(object, ignore_conflicts=False):
        """Add content to the repository.

        If ``ignore_conflicts`` is True data can be overwritten
        unconditionally.  Otherwise care is taken to not overwrite data already
        written by other users or processes.

        Raises TypeError if `object` is not adaptable to IResource.
        Raises ValueError if `object` does not have a uniqueId assigned.
        Raises ConflictError if there was a conflict.

        An IBeforeObjectAddEvent is sent before the object is added to the
        repository.

        """


class IRepositoryContent(zope.interface.Interface):
    """Marker interface for content in the repository.

    Content, which is checked out does *not* provide this interface.

    """


class IDAVContent(zeit.cms.interfaces.ICMSContent):
    """Marker interface for content which originates in this repository."""


class IUnknownResource(IDAVContent):
    """Unknown resource content.

    When an object in the repository cannot be identified or there is no way to
    create a suitable ICMSContent an object implementing IUnknownResource
    may be used.

    """

    type = zope.interface.Attribute("Raw type info got from connector.")


class ICollection(zope.app.container.interfaces.IContainer):
    """A collection."""


class IFolder(ICollection, IDAVContent):
    """A normal folder in the cms."""


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


class IFile(IDAVContent,
            zope.file.interfaces.IFile):
    """A file like object in the CMS."""


class IAutomaticallyRenameable(zope.interface.Interface):
    """Indicate if an object can be renamed automatically.

    This interface is used for objects which do not have their final name, yet.
    For instance when the name should be determined automatically from the
    object's title but the object needs to be added to the repository before
    the title becomes available, it is useful to be able to rename the object
    later.

    NOTE: Renaming is only considered to be a change in the *name*, not in the
    location (aka directory/folder).

    """

    renamable = zope.schema.Bool(title=u'Object renamable?')
    rename_to = zope.schema.TextLine(
        title=_("New file name"),
        required=False,
        constraint=zeit.cms.interfaces.valid_name)
