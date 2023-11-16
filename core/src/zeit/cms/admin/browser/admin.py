from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.admin.interfaces
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zope.formlib.form


class EditFormCI(zeit.cms.browser.form.EditForm):
    form_fields = zope.formlib.form.Fields(
        zeit.cms.admin.interfaces.IAdjustSemanticPublish
    ) + zope.formlib.form.Fields(zeit.cms.workflow.interfaces.IPublishInfo).select(
        'date_print_published'
    )

    # Without field group it will look weird when context is an Article.
    field_groups = (
        gocept.form.grouped.RemainingFields(_('admin-field-group'), 'column-left-small'),
    )

    def __init__(self, context, request):
        super().__init__(context, request)
        for _name, entry in zope.component.getAdapters(
            (context,), zeit.cms.admin.interfaces.IAdditionalFields
        ):
            iface, fields = entry
            self.form_fields += zope.formlib.form.Fields(iface).select(*fields)


class EditFormCO(zeit.cms.browser.form.EditForm):
    form_fields = zope.formlib.form.Fields(
        zeit.cms.content.interfaces.ICachingTime
    ) + zope.formlib.form.Fields(zeit.cms.content.interfaces.ICommonMetadata).select(
        'banner', 'banner_content', 'banner_outer', 'hide_adblocker_notification'
    )

    # Without field group it will look weird when context is an Article.
    field_groups = (
        gocept.form.grouped.RemainingFields(_('admin-field-group'), 'column-left-small'),
    )

    def __init__(self, context, request):
        super().__init__(context, request)
        for _name, entry in zope.component.getAdapters(
            (context,), zeit.cms.admin.interfaces.IAdditionalFieldsCO
        ):
            iface, fields = entry
            self.form_fields += zope.formlib.form.Fields(iface).select(*fields)
