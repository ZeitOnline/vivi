import importlib.resources

from zope.browserpage import ViewPageTemplateFile

from zeit.content.audio.interfaces import IPodcastEpisodeInfo
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces


class Details(zeit.cms.browser.objectdetails.Details):
    """Displays audio details in article view."""

    index = ViewPageTemplateFile(
        str(importlib.resources.files(__package__) / 'object-details-body.pt')
    )

    def __call__(self):
        return self.index()

    @property
    def url(self):
        return self.context.url

    @property
    def duration(self):
        return zeit.cms.browser.widget.readable_duration(self.context.duration)

    @property
    def audio_type(self):
        return self.context.audio_type

    def podcast(self):
        if self.context.audio_type == 'podcast':
            podcast = IPodcastEpisodeInfo(self.context).podcast
            if podcast:
                return podcast.title
        return None

    def dashboard_link(self):
        link = IPodcastEpisodeInfo(self.context).dashboard_link
        return link
