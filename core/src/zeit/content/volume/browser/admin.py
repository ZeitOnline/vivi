import json

import grokcore.component as grok
import zope.browserpage.namedtemplate
import zope.formlib.form
import zope.traversing.browser

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublish
import zeit.cms.admin.browser.admin
import zeit.mediaservice.mediaservice


class PublishAction(zope.formlib.form.Action):
    pass


class RenderPublishAction(zeit.cms.browser.form.RenderLightboxAction):
    grok.context(PublishAction)

    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.target = 'do-' + context.name


class PublishLightbox(zeit.workflow.browser.publish.Publish):
    def create_audio_objects(self):
        return FEATURE_TOGGLES.find('volume_publish_create_audio_objects')


class CreateAudioObjectsLightbox(zeit.workflow.browser.publish.Publish):
    pass


class VolumeAdminForm(zeit.cms.admin.browser.admin.EditFormCI):
    """
    Add an additional Action to the Admin view, which publishes the content
    of a volume.
    """

    extra_actions = zope.formlib.form.Actions()
    extra_actions.append(PublishAction(_('Publish content of this volume'), name='publish-all'))
    extra_actions.append(PublishAction(_('Only create audio objects'), name='create-audio-objects'))

    @property
    def actions(self):
        return list(super().actions) + list(self.extra_actions)


class PublishAll:
    # See zeit.workflow.json.publish.Publish.publish()
    def __call__(self):
        all_content_to_publish = self.context.articles_with_references_for_publishing()
        IPublish(self.context).publish_multiple(
            all_content_to_publish,
            priority=zeit.cms.workflow.interfaces.IPublishPriority(self.context),
        )
        return json.dumps('')


class CreateAudioObjects:
    def __call__(self):
        task = zeit.mediaservice.mediaservice.create_audio_objects.delay(self.context.uniqueId)
        return json.dumps(task.id)
