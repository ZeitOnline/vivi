import zope.formlib.form

import zeit.edit.browser.form


class StudyCourse(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(zeit.campus.interfaces.IStudyCourse).select('course')

    @property
    def prefix(self):
        return 'studycourse.{0}'.format(self.context.__name__)
