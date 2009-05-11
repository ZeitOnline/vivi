# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.view
import zeit.content.cp.browser.rule
import zeit.content.cp.interfaces
import zope.component
import zope.viewlet.manager


class BlockViewletManager(zope.viewlet.manager.WeightOrderedViewletManager):

    def __init__(self, context, request, view):
        super(BlockViewletManager, self).__init__(context, request, view)
        self.validation_class, self.validation_messages = \
            zeit.content.cp.browser.rule.validate(self.context)

    @property
    def css_class(self):
        classes = ['block', 'type-' + self.context.type]
        if self.validation_class:
            classes.append(self.validation_class)
        return ' '.join(classes)


class Add(zeit.content.cp.browser.view.Action):

    type = zeit.content.cp.browser.view.Form('type')

    def update(self):
        factory = zope.component.getAdapter(
            self.context, zeit.content.cp.interfaces.IBlockFactory,
            name=self.type)
        created = factory()
        self.signal('after-reload', 'added', created.__name__)


class Delete(zeit.content.cp.browser.view.Action):

    key = zeit.content.cp.browser.view.Form('key')

    def update(self):
        del self.context[self.key]
        self.signal('before-reload', 'deleted', self.key)


class EditProperties(object):

    def list_block_types(self):
        result = []
        for name, adapter in zope.component.getAdapters(
            (self.context.__parent__,),
            zeit.content.cp.interfaces.IBlockFactory):
            if adapter.title is None:
                continue
            result.append(dict(
                type=name,
                title=adapter.title))
        return result


class SwitchType(object):
    """A generic non-browser view that changes the type of a block"""

    def __init__(self, parent, toswitch, request):
        self.parent = parent
        self.toswitch = toswitch
        self.request = request

    def __call__(self, type):
        order = list(self.parent.keys())
        index = order.index(self.toswitch.__name__)
        del self.parent[self.toswitch.__name__]
        factory = zope.component.getAdapter(
            self.parent, zeit.content.cp.interfaces.IBlockFactory, name=type)
        created = factory()
        order[index] = created.__name__
        self.parent.updateOrder(order)
        return created
