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
            'audio_type') + \
        zope.formlib.form.FormFields(
            zeit.content.audio.interfaces.IAudio).select('__name__')

    audio_fields = gocept.form.grouped.Fields(
        _("Audio"),
        ('title', 'url', 'duration', 'audio_type',),
        css_class='wide-widgets column-left')

    field_groups = (audio_fields,)


class PodcastForm:
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IPodcastEpisodeInfo).select(
            'podcast',
            'image',
            'episode_nr',
            'summary',
            'notes')

    podcast_fields = gocept.form.grouped.Fields(
        _('Podcast Episode Info'),
        ('podcast', 'image', 'episode_nr', 'summary', 'notes'),
        'wide-widgets column-left')

    field_groups = (
        gocept.form.grouped.Fields(
            _('Navigation'), ('__name__',),
            css_class='wide-widgets column-right'),
        Base.audio_fields,
        podcast_fields
    )


class Add(PodcastForm, zeit.cms.browser.form.AddForm):

    title = _('Add audio')
    factory = zeit.content.audio.audio.Audio


class Edit(PodcastForm, zeit.cms.browser.form.EditForm):

    title = _('Edit audio')
    form_fields = PodcastForm.form_fields.omit('__name__')


class Display(PodcastForm, zeit.cms.browser.form.DisplayForm):

    title = _('View audio')
    for_display = True
