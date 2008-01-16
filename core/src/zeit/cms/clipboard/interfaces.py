# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zope.app.container.interfaces

import zeit.cms.interfaces



class IClipboardEntry(zope.interface.Interface):
    """Marker interface for clipboard entries."""


class IObjectReference(IClipboardEntry):
    """Entry in the clipboard referencing an ICMSContent."""

    references = zope.schema.Object(
        zeit.cms.interfaces.ICMSContent,
        title=u"Referenced object",
        description=u"None if the the object reference is invalid.")

    referenced_unique_id = zope.schema.TextLine(
        title=u"Unique Id o the referenced object.",
        readonly=True)



class IClipSchema(zope.interface.Interface):
    """Clip schema."""

    title = zope.schema.TextLine(title=u"Title")


class IClip(IClipSchema, IClipboardEntry,
            zope.app.container.interfaces.IOrderedContainer):
    """A colleciton of entries."""


class IClipboard(IClip):
    """A clipboard is a collection of object references.

    There is actually only one clipboard per user. But users can add containers
    to their clipboard to structure it. The clipboard is persistent, meaning
    unlike the clipboard on windows etc. its contents is not deleted when
    logging out or removed automatically.

    """

    def addContent(reference_object, add_object, name):
        """Add `add_object` to clipboard at position `reference_object`.

        `name` is the proposed local name of add_object in the container. It
        will be used as a hint to the name chooser.

        Clipboards have a hierarichal structure. Depending on which
        `reference_objectobj` is passed the actual adding operation is
        determined:

        1. `reference_object` is an ICMSContent: add after
           `reference_object`
        2. `reference_object` is a (ordered) container (but not ICMSContent):
           insert into `reference_object` at first position.

        raises ValueError if `reference_object` does neither provide
        ICMSContent nor IOrderedContainer.

        """

    def addClip(title):
        """Append a new clip."""

    def moveObject(obj, new_container):
        """Move object to new_container."""
