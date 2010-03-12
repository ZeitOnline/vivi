# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.interfaces
import zeit.cms.browser.form
import zope.formlib.form


class VideoEditForm(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IVideo)


class PlaylistDisplayForm(zeit.cms.browser.form.DisplayForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IPlaylist)


class Thumbnail(zeit.cms.browser.view.Base):

    def __call__(self):
        return self.redirect(self.context.thumbnail, trusted=True)
