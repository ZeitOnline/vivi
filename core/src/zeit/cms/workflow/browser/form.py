from zope.formlib.sequencewidget import ListSequenceWidget
from zope.formlib.widget import CustomWidgetFactory
from zope.formlib.widgets import FileWidget
import zope.formlib.form
import zope.location.interfaces
import zope.site.folder

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IManualPublicationOptions
import zeit.cms.browser.form
import zeit.cms.browser.menu
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workflow.options


class ManualMultiPublishForm(zeit.cms.browser.form.AddForm):
    form_fields = zope.formlib.form.FormFields(
        IManualPublicationOptions,
    )
    form_fields['ignore_services'].custom_widget = CustomWidgetFactory(ListSequenceWidget)
    form_fields['filename'].custom_widget = CustomWidgetFactory(FileWidget)

    @zope.formlib.form.action(_('Add'), condition=zope.formlib.form.haveInputWidgets)
    def handle_add(self, _, data):
        options = zeit.cms.workflow.options.PublicationOptions(**data)
        zeit.cms.workflow.cli.publish_content(options)


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):
    title = _('Publish content')
    viewURL = '@@ManualMultiPublish'
    pathitem = '@@ManualMultiPublish'
