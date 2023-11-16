from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zope.formlib

import zeit.cms.browser.form
import zeit.workflow.browser.form
import zeit.content.audio.audio
import zeit.content.audio.interfaces


class Base:
    form_fields = zope.formlib.form.FormFields(zeit.content.audio.interfaces.IAudio).select(
        'title', 'url', 'duration', 'audio_type'
    ) + zope.formlib.form.FormFields(zeit.content.audio.interfaces.IAudio).select('__name__')

    audio_fields = gocept.form.grouped.Fields(
        _('Audio'),
        (
            'title',
            'duration',
            'audio_type',
        ),
        css_class='wide-widgets column-left',
    )

    audio_file_fields = gocept.form.grouped.Fields(
        _('Audio file'), ('url',), css_class='wide-widgets column-left'
    )

    field_groups = (audio_fields, audio_file_fields)


class PodcastForm:
    form_fields = Base.form_fields + zope.formlib.form.FormFields(
        zeit.content.audio.interfaces.IPodcastEpisodeInfo
    ).select(
        'podcast',
        'episode_nr',
        'url_ad_free',
        'summary',
        'notes',
        'dashboard_link',
    )

    podcast_fields = gocept.form.grouped.Fields(
        _('Podcast Episode Info'),
        ('podcast', 'image', 'episode_nr', 'summary', 'notes'),
        'wide-widgets column-left',
    )

    audio_file_fields = gocept.form.grouped.Fields(
        _('Audio file'),
        (
            'url',
            'url_ad_free',
        ),
        css_class='wide-widgets column-left',
    )

    field_groups = (
        gocept.form.grouped.Fields(
            _('Navigation'), ('__name__', 'dashboard_link'), css_class='wide-widgets column-right'
        ),
        Base.audio_fields,
        audio_file_fields,
        podcast_fields,
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

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        if self.widgets['dashboard_link']:
            self.widgets[
                'dashboard_link'
            ].linkTarget = zeit.content.audio.interfaces.IPodcastEpisodeInfo(
                self.context
            ).dashboard_link


@zope.component.adapter(zeit.content.audio.interfaces.IAudio, zeit.cms.browser.interfaces.ICMSLayer)
@zope.interface.implementer(zeit.workflow.browser.interfaces.IWorkflowForm)
class Workflow(zeit.workflow.browser.form.AssetWorkflow):
    """Publishing for audio is controlled by external provider
    therefore implement the Workflow without the actions.

    We utilize a limitation of zope.formlib:
    Once you list an @action in a subclass,
    no actions are inherited from the base class.

    Less actions equals less buttons.
    """

    @zope.formlib.form.action(_('Save state only'), name='save')
    def handle_save_state(self, action, data):
        super().handle_edit_action.success(data)
