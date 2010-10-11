# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zope.container.interfaces
import zope.interface
import zope.schema
import zope.viewlet.interfaces


class IEditable(zope.interface.Interface):
    """Marker for objects editable through zeit.edit."""


class IElementFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Block type'))

    def __call__():
        """Create block."""


class IElement(zope.interface.Interface):
    """An element which can be instantiated and added to a page."""

    type = zope.interface.Attribute("Type identifier.")


class IBlock(IElement):
    """A block is an element contained in an area.

    In contrast to areas it usually can be edited, sorted, etc.

    """


class IReadContainer(zeit.cms.content.interfaces.IXMLRepresentation,
                zope.container.interfaces.IContained,
                zope.container.interfaces.IReadContainer):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """

class IWriteContainer(zope.container.interfaces.IOrdered):
    """Modify area."""

    def add(item):
        """Add item to container."""

    def __delitem__(key):
        """Remove item."""


class IContainer(IReadContainer, IWriteContainer):
    pass


class IArea(IContainer):
    """Combined read/write interface to areas."""



class IContentViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Viewlets which compose an element."""


class IEditBarViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Vielets which compose an edit bar."""
