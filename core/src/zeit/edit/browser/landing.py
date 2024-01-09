from zope.formlib.form import NoInputData
import zope.component
import zope.formlib.form
import zope.interface

import zeit.cms.browser.form
import zeit.edit.browser.view


class OrderMixin:
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

    @property
    def container(self):
        if self.order == 'after-context':
            return self.context.__parent__
        return self.context

    def get_position_from_order(self, keys):
        if isinstance(self.order, int):
            return self.order
        elif self.order == 'top':
            return 0
        elif self.order == 'bottom':
            return len(keys)
        elif self.order == 'insert-after':
            return keys.index(self.insert_after) + 1
        elif self.order == 'after-context':
            return keys.index(self.context.__name__) + 1
        raise NotImplementedError


class ReloadContainerAction(zeit.edit.browser.view.Action):
    def __call__(self):
        # It seems that each time one accesses a method, the function is bound
        # again, yielding a different object. Since ZCA cares about object
        # identity, we need to ensure we use the same object for register and
        # unregister.
        trigger_reload = self.trigger_reload
        try:
            zope.component.getSiteManager().registerHandler(trigger_reload)
            return super().__call__()
        finally:
            zope.component.getSiteManager().unregisterHandler(trigger_reload)

    @zope.component.adapter(
        zeit.edit.interfaces.IContainer, zope.container.interfaces.IContainerModifiedEvent
    )
    def trigger_reload(self, context, event):
        self.reload(context)


class LandingZone(ReloadContainerAction, OrderMixin):
    """Landing Zone to drop Content or Modules."""

    block_type = NotImplemented
    block_params = zeit.edit.browser.view.Form('block_params', json=True, default={})

    def update(self):
        self.validate_order_params()
        self.validate_block_params()
        self.create_block()
        self.initialize_block()
        self.signal('after-reload', 'added', self.block.__name__)

    def validate_block_params(self):
        if not self.block_params:
            return
        schema = self.block_factory.provided_interface
        if schema is None:
            return  # block not registered via grok, cannot read interface

        errors = []
        data = zeit.cms.browser.form.AttrDict(**self.block_params)
        data['__parent__'] = self.block_factory.context
        for key, value in data.items():
            field = schema[key]
            try:
                field.validate(value)
            except zope.schema.interfaces.ValidationError as e:
                errors.append(e)
        try:
            schema.validateInvariants(data, errors)
        except zope.interface.Invalid:
            pass

        errors.append([x for x in errors if not isinstance(x, NoInputData)])
        if errors:
            raise zope.interface.Invalid(errors)

    @property
    def block_factory(self):
        return zope.component.getAdapter(
            self.container, zeit.edit.interfaces.IElementFactory, name=self.block_type
        )

    def create_block(self):
        position = self.get_position_from_order(self.container.keys())
        self.block = self.block_factory(position=position)

    def initialize_block(self):
        if not self.block_params:
            return
        for key, value in self.block_params.items():
            setattr(self.block, key, value)


class LandingZoneMove(ReloadContainerAction, OrderMixin):
    block_id = zeit.edit.browser.view.Form('id')

    def update(self):
        self.validate_order_params()
        if self.move_to_same_position:
            # The editor expects a reload and will stay busy until the it was
            # send. But since this is a no-op, there will be no reload. Thus we
            # need to send a reload signal anyway, even though nothing has
            # changed to disable the busy state.
            self.reload(self.container)
            return
        self.move_block()

    @property
    def move_to_same_position(self):
        return self.order_from_form == 'insert-after' and self.insert_after == self.block_id

    def move_block(self):
        """Move block to new location.

        If the block was moved inside the same container, i.e. sorted, we need
        to call updateOrder with an adjusted order of keys. If moved between
        containers, a simple delete / insert mechanism will do.

        """
        self.block = self.find_topmost_container(self.container).get_recursive(self.block_id)
        self.old_container = self.block.__parent__

        if self.container == self.old_container:
            keys = list(self.container)  # don't use keys due to security proxy
            keys.remove(self.block.__name__)

            # get pos after remove, otherwise self.block will distort the pos
            pos = self.get_position_from_order(keys)
            keys.insert(pos, self.block.__name__)

            self.container.updateOrder(keys)
        else:
            pos = self.get_position_from_order(self.container.keys())
            del self.old_container[self.block.__name__]
            self.container.insert(pos, self.block)

    def find_topmost_container(self, element):
        container = element
        while True:
            parent = container.__parent__
            if zeit.edit.interfaces.IContainer.providedBy(parent):
                container = parent
            else:
                break
        return container
