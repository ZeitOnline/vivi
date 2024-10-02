import gocept.form.grouped
import zope.formlib

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.content.audio.audio
import zeit.content.audio.interfaces
import zeit.workflow.browser.form


class Base:
    form_fields = zope.formlib.form.FormFields(zeit.content.audio.interfaces.IAudio).select(
        'title', 'url', 'duration', 'audio_type'
    ) + zope.formlib.form.FormFields(zeit.content.audio.interfaces.IAudio).select('__name__')

    audio_fields = gocept.form.grouped.Fields(
        _('Audio'),
        ('title', 'duration', 'audio_type', 'url'),
        css_class='wide-widgets column-left',
    )

    field_groups = (audio_fields,)


class Form:
    _omit_podcast_fields = (
        'podcast',
        'episode_nr',
        'url_ad_free',
        'summary',
        'notes',
        'dashboard_link',
        'url_ad_free',
    )

    _omit_tts_fields = ('article_uuid', 'preview_url', 'checksum')

    form_fields = (
        Base.form_fields
        + zope.formlib.form.FormFields(zeit.content.audio.interfaces.IPodcastEpisodeInfo).select(
            'podcast',
            'episode_nr',
            'url_ad_free',
            'summary',
            'notes',
            'dashboard_link',
        )
        + zope.formlib.form.FormFields(zeit.content.audio.interfaces.ISpeechInfo).select(
            'article_uuid', 'preview_url', 'checksum'
        )
        + zope.formlib.form.FormFields(zeit.cms.content.interfaces.ICommonMetadata).select(
            'teaserTitle', 'teaserSupertitle', 'teaserText'
        )
        + zope.formlib.form.FormFields(zeit.content.image.interfaces.IImages).select('image')
    )

    podcast_fields = gocept.form.grouped.Fields(
        _('Podcast Episode Info'),
        ('podcast', 'episode_nr', 'summary', 'notes'),
        'wide-widgets column-left',
    )

    podcast_host_fields = gocept.form.grouped.Fields(
        _('Podcast Host'),
        ('dashboard_link',),
        'wide-widgets column-left',
    )

    podcast_file_fields = gocept.form.grouped.Fields(
        _('Podcast audio file'),
        ('url_ad_free',),
        css_class='wide-widgets column-left',
    )

    tts_fields = gocept.form.grouped.Fields(
        _('TTS Info'),
        ('article_uuid', 'checksum'),
        'wide-widgets column-left',
    )

    tts_file_fields = gocept.form.grouped.Fields(
        _('TTS audio file'),
        ('preview_url',),
        css_class='wide-widgets column-left',
    )

    teaser_fields = gocept.form.grouped.Fields(
        _('Teaser'),
        ('teaserTitle', 'teaserSupertitle', 'teaserText', 'image'),
        css_class='wide-widgets column-left',
    )

    field_groups = (
        gocept.form.grouped.Fields(
            _('Navigation'), ('__name__',), css_class='wide-widgets column-right'
        ),
        Base.audio_fields,
        podcast_file_fields,
        podcast_fields,
        podcast_host_fields,
        tts_fields,
        tts_file_fields,
        teaser_fields,
    )


class Mixin(Form):
    def __init__(self, context, request):
        super().__init__(context, request)
        if context.audio_type == 'tts':
            self.form_fields = self.form_fields.omit(*self._omit_podcast_fields)
        elif context.audio_type == 'podcast':
            self.form_fields = self.form_fields.omit(*self._omit_tts_fields)
        elif context.audio_type == 'custom':
            self.form_fields = self.form_fields.omit(
                *self._omit_podcast_fields, *self._omit_tts_fields
            )


class Add(Form, zeit.cms.browser.form.AddForm):
    title = _('Add audio')
    factory = zeit.content.audio.audio.Audio


class Edit(Mixin, zeit.cms.browser.form.EditForm):
    title = _('Edit audio')
    form_fields = Form.form_fields.omit('__name__')


class Display(Mixin, zeit.cms.browser.form.DisplayForm):
    title = _('View audio')
    for_display = True

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        if self.widgets.get('dashboard_link'):
            self.widgets[
                'dashboard_link'
            ].linkTarget = zeit.content.audio.interfaces.IPodcastEpisodeInfo(
                self.context
            ).dashboard_link
