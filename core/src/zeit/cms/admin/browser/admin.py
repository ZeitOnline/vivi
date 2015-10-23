import zeit.cms.admin.interfaces
import zeit.cms.browser.form
import zope.formlib.form


class EditForm(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.cms.admin.interfaces.IAdjustSemanticPublish)
