import gocept.form.grouped
import zope.formlib.form

from zeit.cms.content.browser.form import CommonMetadataFormBase
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces
import zeit.content.video.video
import zeit.push.browser.form


class FormFields(zope.formlib.form.FormFields):
    def __init__(self, *args, **kw):
        kw.setdefault('render_context', zope.formlib.interfaces.DISPLAY_UNWRITEABLE)
        super().__init__(*args, **kw)


class Base(zeit.push.browser.form.SocialBase, zeit.push.browser.form.MobileBase):
    form_fields = (
        FormFields(zeit.content.video.interfaces.IVideo).select(
            '__name__',
            'authorships',
            'banner',
            'banner_id',
            'channels',
            'commentSectionEnable',
            'commentsAllowed',
            'commentsPremoderate',
            'keywords',
            'product',
            'ressort',
            'serie',
            'supertitle',
            'teaserText',
            'title',
        )
        + FormFields(zeit.content.video.interfaces.IVideo).select(
            'body',
            'duration',
            'expires',
            'external_id',
            'has_advertisement',
            'kind',
            'type',
            'url',
            'video_still_copyright',
            'width',
        )
        + FormFields(zeit.content.image.interfaces.IImages).select('image')
        + FormFields(zeit.cms.workflow.interfaces.IPublishInfo).select('date_first_released')
        + FormFields(zeit.cms.workflow.interfaces.IModified).select(
            'date_created',
            'date_last_modified',
        )
    )

    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'title', 'teaserText', 'video_still_copyright', 'authorships'),
            css_class='wide-widgets column-left',
        ),
        gocept.form.grouped.Fields(
            _('Navigation'),
            ('__name__', 'keywords', 'serie', 'product', 'ressort'),
            css_class='column-right',
        ),
        gocept.form.grouped.Fields(
            _('Options'),
            (
                'banner',
                'banner_id',
                'breaking_news',
                'commentSectionEnable',
                'commentsAllowed',
                'commentsPremoderate',
                'has_advertisement',
                'kind',
                'type',
                'external_id',
            ),
            css_class='column-right checkboxes',
        ),
        zeit.push.browser.form.SocialBase.social_fields,
        zeit.push.browser.form.MobileBase.mobile_fields,
        CommonMetadataFormBase.auto_cp_fields,
        gocept.form.grouped.Fields(
            _('Video-Thumbnail'), ('image',), css_class='wide-widgets column-left'
        ),
        gocept.form.grouped.Fields(
            _('Texts'),
            ('body',),
            css_class='wide-widgets column-left',
        ),
        gocept.form.grouped.RemainingFields('', css_class='column-left'),
    )


class Add(Base, zeit.cms.browser.form.AddForm):
    title = _('Add Video')
    factory = zeit.content.video.video.Video


class Edit(Base, zeit.cms.browser.form.EditForm):
    title = _('Edit Video')


class Display(Base, zeit.cms.browser.form.DisplayForm):
    title = _('View Video')
