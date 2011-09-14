# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import grokcore.component as grok
import zeit.cms.content.browser.form
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces
import zope.component.hooks
import zope.dublincore.interfaces
import zope.formlib.form

class Edit(zeit.cms.browser.form.EditForm):

    title = _('Video')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.video.interfaces.IVideo,
        zeit.cms.related.interfaces.IRelatedContent,
        zeit.cms.workflow.interfaces.IPublishInfo,
        zope.dublincore.interfaces.IDCTimes,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE
    ).select(
            'supertitle', 'title', 'subtitle', 'teaserText',
            'product', 'ressort', 'keywords', 'serie',
            'dailyNewsletter', 'banner', 'banner_id',
            'breaking_news', 'has_recensions', 'commentsAllowed',
            'related',
            # remaining:
            '__name__',
            'created', 'date_first_released', 'modified', 'expires',
        'thumbnail', 'video_still', 'flv_url')

    field_groups = (
        gocept.form.grouped.Fields(
            _("Texts"),
            ('supertitle', 'title', 'subtitle', 'teaserText'),
            css_class='wide-widgets column-left'),
        gocept.form.grouped.Fields(
            _("Navigation"),
            ('product', 'ressort', 'keywords', 'serie'),
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



@grok.adapter(zeit.content.video.interfaces.IVideo, name='edit.html')
@grok.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'edit.html'
