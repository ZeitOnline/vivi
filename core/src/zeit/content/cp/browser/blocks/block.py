# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zeit.edit.browser.view
import zope.component
import zope.formlib.form
import zope.viewlet.manager


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IBlock).omit('type')


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
            self.parent, zeit.edit.interfaces.IElementFactory, name=type)
        created = factory()
        order[index] = created.__name__
        self.parent.updateOrder(order)
        return created


class Position(object):

    def update(self):
        area = self.context.__parent__
        if zeit.content.cp.interfaces.ILead.providedBy(area):
            keys = self.context.__parent__.keys()
            self.position = keys.index(self.context.__name__) + 1
        else:
            self.position = None
