# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.component


class LandingZone(zeit.edit.browser.view.Action):

    order_from_form = zeit.edit.browser.view.Form('order')

    def update(self):
        if self.order_from_form:
            self.order = self.order_from_form
        self.create_block()
        self.undo_description = _(
            "add '${type}' block", mapping=dict(type=self.block.type))
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
        elif self.order == 'bottom':
            keys.append(new_name)
        elif self.order == 'after-context':
            after = keys.index(self.context.__name__)
            keys.insert(after + 1, new_name)
        else:
            raise NotImplementedError
        return keys
