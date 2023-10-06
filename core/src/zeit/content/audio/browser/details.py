from zope.browserpage import ViewPageTemplateFile

from zeit.content.audio.interfaces import IPodcastEpisodeInfo

import importlib.resources
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces


class Details(zeit.cms.browser.objectdetails.Details):
    """Displays audio details in article view."""

    index = ViewPageTemplateFile(str(importlib.resources.files(
        __package__) / 'object-details-body.pt'))

    def __call__(self):
        return self.index()

    def _readable_duration(self):
        """Returns duration in human readable format.
        From value 160 to to str '2:40'
        """
        if not isinstance(self.context.duration, int):
            return None
        minutes, seconds = divmod(self.context.duration, 60)
        return f"{minutes}:{seconds:02d}"

    @property
    def url(self):
        return self.context.url

    @property
    def duration(self):
        return self._readable_duration()

    @property
    def audio_type(self):
        return self.context.audio_type

    def podcast(self):
        if self.context.audio_type == 'podcast':
            podcast = IPodcastEpisodeInfo(self.context).podcast
            if podcast:
                return podcast.title
        return None
