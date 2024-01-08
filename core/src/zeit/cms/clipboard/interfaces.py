import zope.container.interfaces
import zope.interface
import zope.schema

import zeit.cms.interfaces


class IClipboardEntry(zope.interface.Interface):
    """Marker interface for clipboard entries."""


class IObjectReference(IClipboardEntry):
    """Entry in the clipboard referencing an ICMSContent."""

    references = zope.schema.Object(
        zeit.cms.interfaces.ICMSContent,
        title='Referenced object',
        description='None if the the object reference is invalid.',
    )

    referenced_unique_id = zope.schema.TextLine(
        title='Unique Id o the referenced object.', readonly=True
    )

    title = zope.schema.TextLine(title='Title of the referenced object', readonly=True)

    content_type = zope.schema.TextLine(
        title='Content type of the referenced object', readonly=True
    )


class IClipSchema(zope.interface.Interface):
    """Clip schema."""

    title = zope.schema.TextLine(title='Title')


class IClip(IClipSchema, IClipboardEntry, zope.container.interfaces.IOrderedContainer):
    """A colleciton of entries."""


class IClipboard(IClip):
    """A clipboard is a collection of object references.

    There is actually only one clipboard per user. But users can add containers
    to their clipboard to structure it. The clipboard is persistent, meaning
    unlike the clipboard on windows etc. its contents is not deleted when
    logging out or removed automatically.

    """

    def addContent(reference_object, add_object, name, insert=False):
        """Add `add_object` to clipboard at position `reference_object`.

        `name` is the proposed local name of add_object in the container. It
        will be used as a hint to the name chooser.

        Clipboards have a hierarichal structure:

        1. If the ``reference\\_object`` is a clip *and* insert is True
           content is inserted *into* the container at first position.

        2. In other cases the object is added *after* the reference object.

        raises ValueError if `reference_object` does neither provide
        ICMSContent nor IOrderedContainer.

        raises ValueError if insert==True and reference_object does not provide
        IClip.

        """

    def moveObject(obj, reference_object, insert=False):
        """Move object to after reference_object or into it.

        The new position of obj is the same as if it was added using
        addContent.

        * raises TypeError if obj does not provide IClipboardEntry

        * raises ValueError if reference_object is an ancestor of obj and
          insert == True

        """

    def addClip(title):
        """Append a new clip."""
