import zeit.cms.admin.interfaces
import zope.formlib.form


class View(zope.formlib.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.cms.admin.interfaces.IDateBackSemanticPublish)
