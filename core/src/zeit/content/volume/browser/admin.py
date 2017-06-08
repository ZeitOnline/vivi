from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.admin.browser.admin
import zope.formlib.form


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()

    @property
    def actions(self):
        return (
            list(super(VolumeAdminForm, self).actions) +
            list(self.extra_actions))

    @zope.formlib.form.action(_("Publish content of this volume"),
                              extra_actions)
    def publish_all(self, action, data):
        """
        Publish articles marked as urgent and their boxes.
        """
        all_content_to_publish = \
            self.context.content_with_references_for_publishing()
        IPublish(self.context).publish_multiple(all_content_to_publish)
