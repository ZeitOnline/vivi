import zeit.edit.browser.block
import zeit.edit.browser.view
import zope.formlib.form


class EditProperties(zeit.edit.browser.view.EditBox):

    interface = zeit.content.cp.interfaces.IRegion
    form_fields = zope.formlib.form.Fields()  # XXX implement me


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields()  # XXX implement me
