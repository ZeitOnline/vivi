# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.browserpage import ViewPageTemplateFile
import pkg_resources
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces


class Details(zeit.cms.browser.objectdetails.Details):

    index = ViewPageTemplateFile(pkg_resources.resource_filename(
        'zeit.content.video.browser', 'object-details-body.pt'))

    def __call__(self):
        return self.index()

    @property
    def graphical_preview_url(self):
        return self.context.video_still

