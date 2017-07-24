from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import cgi
import json
import zeit.cms.admin.browser.admin
import zope.browserpage.namedtemplate
import zope.formlib.form
import zope.traversing.browser


class PublishAction(zope.formlib.form.Action):
    pass


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):

    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()
    extra_actions.append(PublishAction(
        _("Publish content of this volume"), lambda *args: None,
        name='publish-all'))

    @property
    def actions(self):
        return (
            list(super(VolumeAdminForm, self).actions) +
            list(self.extra_actions))


@zope.browserpage.namedtemplate.implementation(PublishAction)
def render_publish_action(action):
    if not action.available():
        return ''
    label = action.label
    if isinstance(label, zope.i18nmessageid.Message):
        label = zope.i18n.translate(action.label, context=action.form.request)
    context_url = zope.traversing.browser.absoluteURL(
        action.form.context, action.form.request)
    return (
        u'<button id="{name}" type="button" class="button" onclick='
        u'"zeit.cms.lightbox_form(\'{url}/@@do-publish-all\')">'
        u'{label}</button>'.format(
            name=action.__name__, label=cgi.escape(label, quote=True),
            url=context_url))


class PublishAll(object):

    # See zeit.workflow.json.publish.Publish.publish()
    def __call__(self):
        all_content_to_publish = \
            self.context.content_with_references_for_publishing()
        job = IPublish(self.context).publish_multiple(
            all_content_to_publish,
            priority=zeit.cms.workflow.interfaces.IPublishPriority(
                self.context))
        return json.dumps(job)
