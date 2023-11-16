from zope.browserpage import ViewPageTemplateFile
import importlib.resources
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces


class Details(zeit.cms.browser.objectdetails.Details):
    index = ViewPageTemplateFile(
        str(importlib.resources.files(__package__) / 'object-details-body.pt')
    )

    def __call__(self):
        return self.index()

    @property
    def graphical_preview_url(self):
        return self.context.video_still
