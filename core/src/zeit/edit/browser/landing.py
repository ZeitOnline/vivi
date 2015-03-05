from zeit.cms.i18n import MessageFactory as _
from zope.formlib.form import NoInputData
import zeit.cms.browser.form
import zeit.edit.browser.view
import zope.component
import zope.formlib.form
import zope.interface


class OrderMixin(object):
    """
    Order can have the following values:

    * integer (position) XXX only used as '0', should use 'top' instead
    * `top` (insert at beginning)
    * `bottom` (insert at bottom)
    * `insert-after` (insert after element given by `insert_after` property)
    * `after-context` (XXX bad hack, see below)

    Hack `after-context`: The context parent is used as the container and the
    element is inserted after the context.

    All occurrences of `after-context` should be replaced by `insert-after`.
    """

    order_from_form = zeit.edit.browser.view.Form('order')
    insert_after = zeit.edit.browser.view.Form('insert-after')

    def validate_order_params(self):
        if self.order_from_form:  # XXX make order non-optional and remove this
            self.order = self.order_from_form
        if not hasattr(self, 'order'):
            raise ValueError('Order must be specified!')

    def update_order(self):
        keys = list(self.container)
        keys.remove(self.block.__name__)
        keys = self.add_block_in_order(keys, self.block.__name__)
        self.container.updateOrder(keys)

    @property
    def container(self):
        if self.order == 'after-context':
            return self.context.__parent__
        return self.context

    def add_block_in_order(self, keys, new_name):
        if isinstance(self.order, int):
            keys.insert(self.order, new_name)
        elif self.order == 'top':
            keys.insert(0, new_name)
        elif self.order == 'bottom':
            keys.append(new_name)
        elif self.order == 'insert-after':
            after = keys.index(self.insert_after)
            keys.insert(after + 1, new_name)
        elif self.order == 'after-context':
            after = keys.index(self.context.__name__)
            keys.insert(after + 1, new_name)
        else:
            raise NotImplementedError
        return keys

    def reload(self, container):
        self.signal(
            None, 'reload',
            container.__name__, self.url(container, '@@contents'))


class LandingZone(zeit.edit.browser.view.Action, OrderMixin):
    """Landing Zone to drop Content or Modules.

    """

    block_params = zeit.edit.browser.view.Form(
        'block_params', json=True, default={})

    def update(self):
        self.validate_order_params()
        self.validate_block_params()
        self.create_block()
        self.undo_description = _(
            "add '${type}' block", mapping=dict(type=self.block.type))
        self.initialize_block()
        self.update_order()
        self.signal('after-reload', 'added', self.block.__name__)
        self.reload(self.container)

    def validate_block_params(self):
        if not self.block_params:
            return
        schema = self.block_factory.provided_interface
        if schema is None:
            return  # block not registered via grok, cannot read interface

        errors = []
        data = zeit.cms.browser.form.AttrDict(**self.block_params)
        data['__parent__'] = self.block_factory.context
        try:
            schema.validateInvariants(data, errors)
        except zope.interface.Invalid:
            pass

        errors = [e for e in errors if not isinstance(e, NoInputData)]
        if errors:
            raise zope.interface.Invalid(errors)

    @property
    def block_factory(self):
        return zope.component.getAdapter(
            self.container, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)

    def create_block(self):
        self.block = self.block_factory()

    def initialize_block(self):
        if not self.block_params:
            return
        for key, value in self.block_params.items():
            setattr(self.block, key, value)


class LandingZoneMove(zeit.edit.browser.view.Action, OrderMixin):

    block_id = zeit.edit.browser.view.Form('id')

    def update(self):
        self.validate_order_params()
        if self.move_to_same_position:
            return
        self.move_block()
        self.undo_description = _(
            "move '${type}' block", mapping=dict(type=self.block.type))
        self.update_order()
        self.reload(self.old_container)
        if self.container.__name__ != self.old_container.__name__:
            self.reload(self.container)

    @property
    def move_to_same_position(self):
        return (self.order_from_form == 'insert-after'
                and self.insert_after == self.block_id)

    def move_block(self):
        self.block = self.find_topmost_container(
            self.context).get_recursive(self.block_id)
        self.old_container = self.block.__parent__
        del self.old_container[self.block.__name__]
        self.context.add(self.block)

    def find_topmost_container(self, element):
        container = element
        while True:
            parent = container.__parent__
            if zeit.edit.interfaces.IContainer.providedBy(parent):
                container = parent
            else:
                break
        return container
