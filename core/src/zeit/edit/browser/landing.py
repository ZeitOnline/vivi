# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.component


class LandingZone(zeit.edit.browser.view.Action):
    """Landing Zone to drop Content or Modules.

    Order can have the following values:

    * integer (position)
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
    block_params = zeit.edit.browser.view.Form(
        'block_params', json=True, default={})

    def update(self):
        if self.order_from_form:  # XXX make order non-optional and remove this
            self.order = self.order_from_form
        if not hasattr(self, 'order'):
            raise ValueError('Order must be specified!')
        self.validate_params()
        self.create_block()
        self.undo_description = _(
            "add '${type}' block", mapping=dict(type=self.block.type))
        self.initialize_block()
        self.update_order()
        self.signal('after-reload', 'added', self.block.__name__)
        self.signal(
            None, 'reload',
            self.create_in.__name__, self.url(self.create_in, '@@contents'))

    def validate_params(self):
        pass

    def create_block(self):
        factory = zope.component.getAdapter(
            self.create_in, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)
        self.block = factory()

    def initialize_block(self):
        for key, value in self.block_params.items():
            setattr(self.block, key, value)

    def update_order(self):
        keys = list(self.create_in)
        keys.remove(self.block.__name__)
        keys = self.add_block_in_order(keys, self.block.__name__)
        self.create_in.updateOrder(keys)

    @property
    def create_in(self):
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
