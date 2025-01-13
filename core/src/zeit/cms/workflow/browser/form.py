import gocept.form.grouped
import zope.formlib.form
import zope.location.interfaces
import zope.site.folder

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IManualPublicationOptions
import zeit.cms.browser.form
import zeit.cms.browser.menu
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces


class ManualMultiPublishForm(zeit.cms.browser.form.FormBase, gocept.form.grouped.DisplayForm):
    form_fields = zope.formlib.form.FormFields(
        IManualPublicationOptions,
    )

    def _get_widgets(self, form_fields, ignore_request):
        return zope.formlib.form.setUpInputWidgets(
            form_fields, self.prefix, self.context, self.request, ignore_request=ignore_request
        )

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, _, data):
        to_publish = data['unique_ids']
        if not to_publish:
            return
        zeit.cms.workflow.cli.publish_content.delay(data)


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):
    title = _('Publish content')
    viewURL = '@@ManualMultiPublish'
    pathitem = '@@ManualMultiPublish'
