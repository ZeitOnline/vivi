from zeit.cms.i18n import MessageFactory as _
import inspect
import zeit.cms.interfaces
import zope.container.interfaces
import zope.file.interfaces
import zope.interface
import zope.lifecycleevent
import zope.schema


class IBeforeObjectAddEvent(zope.interface.interfaces.IObjectEvent):
    """An event sent before an object will be added to the repository."""


@zope.interface.implementer(IBeforeObjectAddEvent)
class BeforeObjectAddEvent(zope.interface.interfaces.ObjectEvent):
    """An event sent before an object will be added to the repository."""


class IAfterObjectConstructedEvent(zope.interface.interfaces.IObjectEvent):
    """An event sent after an ICMSContent is constructed from a resource."""

    resource = zope.interface.Attribute(
        'IResource the object was constructed from')


@zope.interface.implementer(IAfterObjectConstructedEvent)
class AfterObjectConstructedEvent(zope.interface.interfaces.ObjectEvent):
    """An event sent after an ICMSContent is constructed from a resource."""

    def __init__(self, obj, resource):
        self.object = obj
        self.resource = resource


class IBeforeObjectRemovedEvent(zope.lifecycleevent.IObjectRemovedEvent):
    """An event sent after an ICMSContent is removed from a resource."""


@zope.interface.implementer(IBeforeObjectRemovedEvent)
class BeforeObjectRemovedEvent(zope.lifecycleevent.ObjectRemovedEvent):
    """An event sent after an ICMSContent is removed from a resource."""


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


class ICollection(zope.container.interfaces.IContainer):
    """A collection."""


class IFolder(ICollection, IDAVContent):
    """A normal folder in the cms."""


class INonRecursiveCollection(ICollection):
    """A collection that should not be recursively iterated, e.g. for indexing.
    This is a semantic marker, i.e. we probably have children etc. as normal,
    but it just doesn't make sense to traverse them.

    Typical (and currently only) example:
    zeit.newsletter.interfaces.INewsletterCategory
    """


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


class AlreadyExists(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


class NotFound(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


def valid_name(value):
    # XXX this makes quite a few assumptions, e.g. that the field's context as
    # an attribute uniqueId, so it's probably not generally applicable.
    if not zeit.cms.interfaces.valid_name(value):
        return False
    field = inspect.stack()[2][0].f_locals['self']
    context = field.context
    context = zeit.cms.interfaces.ICMSContent(context.uniqueId)
    container = context.__parent__
    if value in container:
        raise AlreadyExists(
            _('"${name}" already exists.', mapping=dict(name=value)))
    return True


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

    renameable = zope.schema.Bool(title=u'Object renameable?')
    rename_to = zope.schema.TextLine(
        title=_("New file name"),
        required=False,
        constraint=valid_name)

    uniqueId = zope.interface.Attribute('Current uniqueId')


class IObjectReloadedEvent(zope.interface.interfaces.IObjectEvent):
    """An event sent when a reload action is triggered through the UI, so we
    can differentiate from zeit.connector.interfaces.ResourceInvaliatedEvent,
    which is triggered by the invalidator, too.
    """


@zope.interface.implementer(IObjectReloadedEvent)
class ObjectReloadedEvent(zope.interface.interfaces.ObjectEvent):
    pass
