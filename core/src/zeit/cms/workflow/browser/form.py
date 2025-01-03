import grokcore.component as grok
import zope.formlib.form
import zope.location.interfaces
import zope.site.folder

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.menu

from .interfaces import IManualMultiPublish


class ManualMultiPublish:
    force_unpublished = False
    force_unchanged = False
    skip_deps = False
    use_checkin_hooks = False
    use_publish_hooks = False
    ignore_services = ()
    wait_tms = False
    skip_tms_enrich = False
    dlps = False
    unique_ids = ''


@grok.implementer(IManualMultiPublish)
@grok.adapter(zope.site.folder.Folder)
def manual_multi_publish_factory(_):
    return ManualMultiPublish()


class ManualMultiPublishForm(zeit.cms.browser.form.EditForm):
    form_fields = zope.formlib.form.FormFields(IManualMultiPublish)

    @zope.formlib.form.action(_('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        super().handle_edit_action.success(data)


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):
    title = _('Publish content')
    viewURL = '@@ManualMultiPublish'
    pathitem = '@@ManualMultiPublish'
