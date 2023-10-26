from zope.browserpage import ViewPageTemplateFile
import importlib.resources
import zeit.cms.browser.objectdetails
import zeit.edit.browser.form
import zope.formlib.form
import zope.formlib.interfaces


class ReferenceDetailsHeading(zeit.cms.browser.objectdetails.Details):

    template = ViewPageTemplateFile(str((importlib.resources.files(
        'zeit.cms.browser') / 'object-details-heading.pt')))

    def __init__(self, context, request):
        super().__init__(context.target, request)

    def __call__(self):
        return self.template()


class Edit(zeit.edit.browser.form.InlineForm):

    legend = ''

    form_fields = zope.formlib.form.FormFields(
        zeit.content.author.interfaces.IAuthorBioReference,
        # support read-only mode, see
        # zeit.content.article.edit.browser.form.FormFields
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
        'biography')

    @property
    def prefix(self):
        return 'reference-details-%s' % self.context.target.uniqueId
