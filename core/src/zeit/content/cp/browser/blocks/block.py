import zeit.cms.browser.widget
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zope.component
import zope.formlib.form


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(ViewletManager, self).css_class
        visible = 'block-visible-off' if not self.context.visible else ''
        return ' '.join(['editable-module', visible, classes])


class EditCommon(zeit.content.cp.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IBlock).select(
            'supertitle', 'title',
            'read_more', 'read_more_url',
            'background_color')
    form_fields['background_color'].custom_widget = (
        zeit.cms.browser.widget.ColorpickerWidget)


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
        if zeit.content.cp.interfaces.IArea.providedBy(area):
            keys = self.context.__parent__.keys()
            self.position = keys.index(self.context.__name__) + 1
        else:
            self.position = None
