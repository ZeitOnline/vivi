import json

import grokcore.component as grok
import zope.browserpage.namedtemplate
import zope.formlib.form
import zope.traversing.browser

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.admin.browser.admin
import zeit.mediaservice.mediaservice


class PublishAction(zope.formlib.form.Action):
    pass


class RenderPublishAction(zeit.cms.browser.form.RenderLightboxAction):
    grok.context(PublishAction)
    target = 'do-publish-all'


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):
    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()
    extra_actions.append(PublishAction(_('Publish content of this volume'), name='publish-all'))

    @property
    def actions(self):
        return list(super().actions) + list(self.extra_actions)


class PublishAll:
    # See zeit.workflow.json.publish.Publish.publish()
    def __call__(self):
        all_content_to_publish = self.context.articles_with_references_for_publishing()
        tasks = IPublish(self.context).publish_multiple(
            all_content_to_publish,
            priority=zeit.cms.workflow.interfaces.IPublishPriority(self.context),
        )
        return json.dumps(','.join((task.id for task in tasks)))


class CreateAudioObjects:
    def __call__(self):
        task = zeit.mediaservice.mediaservice.create_audio_objects.delay(self.context.uniqueId)
        return json.dumps(task.id)
