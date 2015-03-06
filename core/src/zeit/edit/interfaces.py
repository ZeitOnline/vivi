from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.container.interfaces
import zope.interface
import zope.schema
import zope.viewlet.interfaces


BLOCK_NAMESPACE = 'http://block.vivi.zeit.de/'


class IEditable(zope.interface.Interface):
    """Marker for objects editable through zeit.edit."""


class IElementFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Block type'))

    def __call__():
        """Create block."""


class IElement(zeit.cms.content.interfaces.IXMLRepresentation):
    """An element which can be instantiated and added to a page."""

    type = zope.interface.Attribute("Type identifier.")
    uniqueId = zope.interface.Attribute("Only used as source for references")


class IBlock(IElement, zope.container.interfaces.IContained):
    """A block is an element contained in an area.

    In contrast to areas it usually can be edited, sorted, etc.

    """

    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent_ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)


class IUnknownBlock(IBlock):
    """A block that is not supported by zeit.cms.
    It is passed through the system opaquely.
    """


class IReadContainer(zeit.cms.content.interfaces.IXMLRepresentation,
                     zope.container.interfaces.IContained,
                     zope.container.interfaces.IReadContainer,
                     IElement):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """

    def index(value):
        """Determine position of the given value among self.values,
        even when value does not have a __name__ yet."""

    def slice(start, end):
        """Return list of blocks between the names start and end, inclusive."""

    def get_recursive(key, default):
        """Return item for key. If not found in self, search recursively in
        IContainers contained in self.
        """


class IWriteContainer(zope.container.interfaces.IOrdered):
    """Modify area."""

    def add(item):
        """Add item to container."""

    def create_item(type_):
        """Create item of given type and add it to the end of the container."""

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


# Rule and validation system

class IRuleGlobs(zope.interface.Interface):
    """Adapt to this to convert the context to a dictionary of things of
    interest to an IRule XXX docme"""


class IRuleGlob(zope.interface.Interface):
    """XXX docme"""


class IValidator(zope.interface.Interface):
    """Adapt an object to validate it with the rule system."""

    status = zope.schema.TextLine(
        title=u"Validation status: {None, warning, error}")

    messages = zope.schema.List(
        title=u"List of error messages.")


class IRulesManager(zope.interface.Interface):
    """Collects all validation rules."""

    rules = zope.schema.List(title=u"A list of rules.")


class IUndo(zope.interface.Interface):

    history = zope.interface.Attribute(
        """A list of history entries. A history entry is a dict with the keys:
        tid: transaction identifier which can be passed to revert()
        description: a human-readable description what happened in this
        transaction

        The entries are sorted with the most recent one first.
        """)

    def revert(tid):
        """Revert the object to the state it had before the given transaction
        id (i.e. undo any changes made up to and including this transaction)"""


class IFoldable(zope.interface.Interface):
    """Marker for blocks that can be folded in the UI."""


def unique_name_invariant(data):
    """Bad hack, this invariant is called manually from form.

    We must have access to the object in question, thus we enrich the given
    data with __context__ beforehand. Since validations only get data that
    matches a form_field they have, we must call the invariant manually by
    overwriting `validate`.

    """
    context = getattr(data, '__context__', None)
    if context is None:
        return
    for name, element in context.__parent__.items():
        if context == element:
            continue
        if data.__name__ == name:
            raise zeit.cms.interfaces.ValidationError(
                _("Given name {name} is not unique inside parent {parent}."
                  .format(name=data.__name__,
                          parent=context.__parent__.__name__)))
