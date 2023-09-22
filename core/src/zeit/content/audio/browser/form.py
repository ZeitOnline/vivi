from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zope.formlib

import zeit.cms.browser.form
import zeit.content.audio.audio
import zeit.content.audio.interfaces


class Base:

    form_fields = zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IAudio).select(
            'title',
            'url',
            'duration',
            'audio_type')

    field_groups = (
        gocept.form.grouped.Fields(
            _("Audio"),
            ('title', 'url', 'duration', 'audio_type',),
            css_class='wide-widgets column-left'),)


class PodcastInfo:
    form_fields = zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IPodcastEpisodeInfo).select(
            'podcast',
            'image',
            'episode_nr',
            'summary',
            'notes')

    field_groups = (
        gocept.form.grouped.Fields(
            _('Podcast Episode Info'),
            ('podcast', 'image', 'episode_nr', 'summary', 'notes'),
            'wide-widgets column-left'),)


class Add(Base, zeit.cms.browser.form.AddForm):

    title = _('Add audio')
    factory = zeit.content.audio.audio.Audio
    form_fields = Base.form_fields + PodcastInfo.form_fields + \
        zope.formlib.form.FormFields(
            zeit.content.audio.interfaces.IAudio).select('__name__')

    field_groups = (
        (gocept.form.grouped.Fields(
            _('Navigation'), ('__name__',),
            css_class='wide-widgets column-right'),)
        + Base.field_groups + PodcastInfo.field_groups)


class Edit(Base, zeit.cms.browser.form.EditForm):

    title = _('Edit audio')
    form_fields = Base.form_fields.omit('__name__')


class Display(Base, zeit.cms.browser.form.DisplayForm):

    title = _('View audio')
    form_fields = Base.form_fields.omit('__name__') + PodcastInfo.form_fields
    for_display = True
