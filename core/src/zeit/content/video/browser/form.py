# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import copy
import gocept.form.grouped
import urllib2
import zeit.cms.browser.form
import zeit.content.video.interfaces
import zope.component.hooks
import zope.formlib.form


class Edit(zeit.cms.browser.form.EditForm):

    title = _('Edit video')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.video.interfaces.IVideo)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Texts"),
            ('supertitle', 'title', 'subtitle', 'teaserText'),
            css_class='wide-widgets column-left'),
        gocept.form.grouped.Fields(
            _("Navigation"),
            ('product_id', 'ressort', 'keywords', 'serie'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Options"),
            ('dailyNewsletter', 'banner', 'banner_id',
             'breaking_news', 'has_recensions', 'commentsAllowed'),
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
            return self.url(zope.component.hooks.getSite())
