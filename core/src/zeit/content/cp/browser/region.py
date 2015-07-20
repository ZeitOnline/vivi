import zeit.edit.browser.view
import zope.formlib.form


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRegion).select('title', 'visible_mobile')
