import zope.component
import zope.interface

from zeit.cms.i18n import MessageFactory as _
from zeit.content.audio.interfaces import IAudio, IPodcastEpisodeInfo
import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased


class AudioWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    def can_publish(self):
        status = super().can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        if not self.context.url:
            self.error_messages = (
                _(
                    'Could not publish ${name}. Audio URL is missing',
                    mapping={'name': self.context.uniqueId},
                ),
            )
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS


class PodcastWorkflow(AudioWorkflow):
    def can_publish(self):
        status = super().can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        if not IPodcastEpisodeInfo(self.context).is_published:
            self.error_messages = (
                _(
                    'Could not publish ${name}. Podcast Episode is not published by Provider',
                    mapping={'name': self.context.uniqueId},
                ),
            )
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS

    def can_retract(self):
        if IPodcastEpisodeInfo(self.context).is_published:
            self.error_messages = (
                _(
                    'Could not retract ${name}. Podcast Episode is published by Provider',
                    mapping={'name': self.context.uniqueId},
                ),
            )
            return zeit.cms.workflow.interfaces.CAN_RETRACT_ERROR
        return zeit.cms.workflow.interfaces.CAN_RETRACT_SUCCESS


@zope.component.adapter(IAudio)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublishInfo)
def dispatch_workflow_via_audio_type(audio_context):
    match audio_context.audio_type:
        case 'podcast':
            workflow = PodcastWorkflow(audio_context)
        case _:
            workflow = AudioWorkflow(audio_context)
    return workflow
