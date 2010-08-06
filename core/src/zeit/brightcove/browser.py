# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component
import zeit.brightcove.interfaces
import zeit.cms.browser.form
import zope.formlib.form
import zope.site.hooks
import zope.traversing.browser.absoluteurl
import zope.traversing.browser.interfaces


class VideoEditForm(zeit.cms.browser.form.EditForm):

    title = _('Edit video')

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IVideo).omit('__name__', 'thumbnail')

    field_groups = (
        gocept.form.grouped.Fields(
            _("Texts"),
            ('supertitle', 'title', 'subtitle', 'teaserText'),
            css_class='wide-widgets column-left'),
        gocept.form.grouped.Fields(
            _("Navigation"),
            ('id', 'ressort', 'keywords', 'serie'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Options"),
            ('item_state', 'expires', 'dailyNewsletter', 'banner', 'banner_id',
             'breaking_news', 'has_recensions', 'product_id', 'allow_comments'),
            css_class='column-right checkboxes'),
        gocept.form.grouped.Fields(
            _('Teaser elements'),
            ('related',),
            'wide-widgets full-width'),
    )

    _redir = False

    @zope.formlib.form.action(
        _('Apply'), condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        self.applyChanges(data)

    @zope.formlib.form.action(
        _('Apply and go to search'),
        condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_and_serach_action(self, action, data):
        self.applyChanges(data)
        self._redir = True

    def nextURL(self):
        if self._redir:
            return self.url(zope.site.hooks.getSite())


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
