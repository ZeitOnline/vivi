import zope.container.contained
import zope.container.interfaces
import zope.interface
import zope.location.interfaces
import zope.schema
import zope.viewlet.interfaces

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.cms.interfaces


BLOCK_NAMESPACE = 'http://block.vivi.zeit.de/'


class IElementFactory(zope.interface.Interface):
    title = zope.schema.TextLine(title=_('Block type'))

    def __call__(position=None):
        """Create block at position."""


class IElement(zeit.cms.content.interfaces.IXMLRepresentation):
    """An element which can be instantiated and added to a page."""

    type = zope.interface.Attribute('Type identifier.')
    uniqueId = zope.interface.Attribute('Only used as source for references')


class IBlock(IElement, zope.location.interfaces.IContained):
    """A block is an element contained in an area.

    In contrast to areas it usually can be edited, sorted, etc.

    """

    # Use a schema field so the security can declare it as writable,
    # since in ILocation __parent__ is only an Attribute.
    __parent__ = zope.schema.Object(IElement)


class IUnknownBlock(IBlock):
    """A block that is not supported by zeit.cms.
    It is passed through the system opaquely.
    """


class IReadContainer(
    zeit.cms.content.interfaces.IXMLRepresentation,
    zope.location.interfaces.IContained,
    zope.container.interfaces.IReadContainer,
    IElement,
):
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

    def filter_values(*interfaces):
        """Returns only those items in self.values() that provide any of
        the given interfaces.
        """

    def find_first(interface):
        """Returns the first item in self.values() that provides the given
        interface; None if no such item exists.
        """


class IWriteContainer(zope.container.interfaces.IOrdered):
    """Modify area."""

    def add(item):
        """Add item to container."""

    def insert(position, item):
        """Add an item at the given position to the container."""

    def create_item(type_, position=None):
        """Create item of given type and add it to the end of the container.

        If position is given, the item will be sorted to the correct position
        afterwards.

        """

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

    status = zope.schema.TextLine(title='Validation status: {None, warning, error}')

    messages = zope.schema.List(title='List of error messages.')


class IRulesManager(zope.interface.Interface):
    """Collects all validation rules."""

    rules = zope.schema.List(title='A list of rules.')


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
                _(
                    'Given name {name} is not unique inside parent {parent}.'.format(
                        name=data.__name__, parent=context.__parent__.__name__
                    )
                )
            )


class IOrderUpdatedEvent(zope.container.interfaces.IContainerModifiedEvent):
    old_order = zope.interface.Attribute('List of keys of the previous order')


@zope.interface.implementer(IOrderUpdatedEvent)
class OrderUpdatedEvent(zope.container.contained.ContainerModifiedEvent):
    def __init__(self, context, *old_order):
        super().__init__(context)
        self.old_order = old_order


class IElementReferences(zope.interface.Interface):
    """
    Iterate over the elements which are referenced in the body.
    """

    def __iter__():
        pass
