import zeit.edit.browser.block
import zeit.edit.browser.view
import zope.formlib.form


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(ViewletManager, self).css_class
        return ' '.join(['editable-region', classes])


class EditProperties(zeit.edit.browser.view.EditBox):

    interface = zeit.content.cp.interfaces.IRegion
    form_fields = zope.formlib.form.Fields()  # XXX implement me


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields()  # XXX implement me
