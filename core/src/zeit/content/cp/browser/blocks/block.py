# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.browser.rule
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zope.app.pagetemplate
import zope.component
import zope.formlib.form
import zope.viewlet.manager


class BlockViewletManager(zope.viewlet.manager.WeightOrderedViewletManager):

    def __init__(self, context, request, view):
        super(BlockViewletManager, self).__init__(context, request, view)
        self.validation_class, self.validation_messages = (
            zeit.content.cp.browser.rule.validate(self.context))

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
            self.context, zeit.edit.interfaces.IElementFactory,
            name=self.type)
        created = factory()
        self.signal('after-reload', 'added', created.__name__)


class Delete(zeit.content.cp.browser.view.Action):

    key = zeit.content.cp.browser.view.Form('key')

    def update(self):
        del self.context[self.key]
        self.signal('before-reload', 'deleted', self.key)
        self.signal(
            None, 'reload', self.context.__name__, self.url(self.context,
                                                            '@@contents'))


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
