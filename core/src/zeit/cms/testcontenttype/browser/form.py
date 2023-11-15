import zeit.cms.content.browser.form
import zeit.cms.testcontenttype.interfaces
import zope.formlib.form


class Base:
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.testcontenttype.interfaces.IExampleContentType
    ).omit('xml')


class Edit(Base, zeit.cms.content.browser.form.CommonMetadataEditForm):
    pass
