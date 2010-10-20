# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.browser.view
import zope.component

class LandingZone(zeit.edit.browser.view.Action):

    def update(self):
        self.create_block()
        self.initialize_block()
        self.update_order()
        self.signal('after-reload', 'added', self.block.__name__)
        self.signal(
            None, 'reload',
            self.create_in.__name__, self.url(self.create_in, '@@contents'))

    def create_block(self):
        factory = zope.component.getAdapter(
            self.create_in, zeit.edit.interfaces.IElementFactory,
            name=self.block_type)
        self.block = factory()

    def initialize_block(self):
        pass

    def update_order(self):
        order = list(self.create_in)
        order.remove(self.block.__name__)
        order = self.get_order(order, self.block.__name__)
        self.create_in.updateOrder(order)

    @property
    def create_in(self):
        if self.order == 'after-context':
            return self.context.__parent__
        return self.context

    def get_order(self, order, new_name):
        if isinstance(self.order, int):
            order.insert(self.order, new_name)
        elif self.order == 'after-context':
            after = order.index(self.context.__name__)
            order.insert(after + 1, new_name)
        else:
            raise NotImplementedError
        return order
