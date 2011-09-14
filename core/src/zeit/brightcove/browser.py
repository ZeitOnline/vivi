# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import zeit.brightcove.interfaces
import zeit.cms.browser.form
import zope.formlib.form
import zope.traversing.browser.absoluteurl


class PlaylistDisplayForm(zeit.cms.browser.form.DisplayForm):

    title = _('View playlist')

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IPlaylist)


class Thumbnail(zeit.cms.browser.view.Base):

    @property
    def thumbnail_url(self):
        return self.context.thumbnail

    def __call__(self):
        return self.redirect(self.thumbnail_url, trusted=True)


class ThumbnailURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    def __str__(self):
        if self.context.thumbnail_url:
            return self.context.thumbnail_url
        raise TypeError("No Thumbnail")


class Still(zeit.cms.browser.view.Base):

    @property
    def video_still_url(self):
        return self.context.video_still

    def __call__(self):
        return self.redirect(self.video_still_url, trusted=True)


class StillURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    def __str__(self):
        if self.context.video_still_url:
            return self.context.video_still_url
        raise TypeError("No still url")


@grokcore.component.adapter(zeit.brightcove.interfaces.IBrightcoveContent,
                        basestring)
@grokcore.component.implementer(zeit.cms.browser.interfaces.IPreviewURL)
def preview_url(content, preview_type):
    return content.uniqueId
