# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.browser.rule
import zeit.edit.browser.view
import zeit.content.cp.interfaces
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.viewlet.manager


class EditCommon(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'block.edit-common.pt')

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IBlock).omit('type')

    close = False

    @property
    def form(self):
        return super(EditCommon, self).template

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.close = True
        # XXX: dear zope.formlib, are you serious?!
        return super(EditCommon, self).handle_edit_action.success(data)


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
