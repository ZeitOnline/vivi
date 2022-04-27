import zeit.content.cp.browser.view
import zope.formlib.form


class EditCommon(zeit.content.cp.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRegion).select('title')
