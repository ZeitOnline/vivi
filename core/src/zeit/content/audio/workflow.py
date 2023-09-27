from zeit.cms.i18n import MessageFactory as _

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased

from zeit.content.audio.interfaces import IAudio, IPodcastEpisodeInfo


class AudioWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):

    def can_publish(self):
        status = super().can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        if not self.context.url:
            self.error_messages = (
                _('Could not publish %s.'
                  ' Audio URL is missing' % self.context.uniqueId),)
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS


class PodcastWorkflow(AudioWorkflow):

    def can_publish(self):
        status = super().can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        if not IPodcastEpisodeInfo(self.context).is_published:
            self.error_messages = (
                _('Could not publish %s. Podcast Episode is '
                  'not published by Provider' % self.context.uniqueId),)
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS


@zope.component.adapter(IAudio)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def dispatch_workflow_via_audio_type(audio_context):
    match audio_context.audio_type:
        case 'podcast':
            workflow = PodcastWorkflow(audio_context)
        case _:
            workflow = AudioWorkflow(audio_context)
    return workflow
