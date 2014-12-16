import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.formlib.form


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRegion).select('title', '__name__')

    def validate(self, action, data):
        errors = super(EditCommon, self).validate(action, data)
        try:
            data['__context__'] = self.context
            zeit.edit.interfaces.unique_name_invariant(
                zeit.cms.browser.form.AttrDict(**data))
        except Exception as e:
            errors.append(e)
        return errors
