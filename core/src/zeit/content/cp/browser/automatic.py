import zeit.cms.browser.form
import zope.formlib.form


class Edit(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutomaticRegion).select(
            'count', 'query', 'automatic')

    def __init__(self, context, request):
        super(Edit, self).__init__(context['lead'], request)
