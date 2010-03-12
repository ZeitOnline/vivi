# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.brightcove.interfaces
import zeit.cms.browser.form
import zope.formlib.form


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
            ('item_state', 'dailyNewsletter', 'banner', 'banner_id',
             'breaking_news', 'has_recensions', 'product_id'),
            css_class='column-right checkboxes'),
        gocept.form.grouped.Fields(
            _('Teaser elements'),
            ('related',),
            'wide-widgets full-width'),
    )

class PlaylistDisplayForm(zeit.cms.browser.form.DisplayForm):

    title = _('View playlist')

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IPlaylist)


class Thumbnail(zeit.cms.browser.view.Base):

    def __call__(self):
        return self.redirect(self.context.thumbnail, trusted=True)
