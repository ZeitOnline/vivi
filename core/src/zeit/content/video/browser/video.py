import gocept.form.grouped
import zope.formlib.form

from zeit.cms.content.browser.form import CommonMetadataFormBase
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.related.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces
import zeit.push.browser.form


class Base(zeit.push.browser.form.SocialBase, zeit.push.browser.form.MobileBase):
    form_fields = zope.formlib.form.FormFields(
        zeit.content.video.interfaces.IVideo,
        zeit.content.image.interfaces.IImages,
        zeit.cms.workflow.interfaces.IPublishInfo,
        zeit.cms.workflow.interfaces.IModified,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE,
    ).select(
        'supertitle',
        'title',
        'teaserText',
        'product',
        'ressort',
        'keywords',
        'serie',
        'banner',
        'banner_id',
        'type',
        'commentsAllowed',
        'commentsPremoderate',
        'channels',
        'video_still_copyright',
        'has_advertisement',
        # remaining:
        '__name__',
        'image',
        'date_created',
        'date_first_released',
        'date_last_modified',
        'expires',
        'authorships',
    )

    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'title', 'teaserText', 'video_still_copyright'),
            css_class='wide-widgets column-left',
        ),
        gocept.form.grouped.Fields(
            _('Navigation'), ('product', 'ressort', 'keywords', 'serie'), css_class='column-right'
        ),
        gocept.form.grouped.Fields(
            _('Options'),
            (
                'banner',
                'banner_id',
                'breaking_news',
                'commentsAllowed',
                'commentsPremoderate',
                'has_advertisement',
                'type',
            ),
            css_class='column-right checkboxes',
        ),
        zeit.push.browser.form.SocialBase.social_fields,
        zeit.push.browser.form.MobileBase.mobile_fields,
        CommonMetadataFormBase.auto_cp_fields,
        gocept.form.grouped.Fields(
            _('Video-Thumbnail'), ('image',), css_class='wide-widgets column-left'
        ),
        gocept.form.grouped.RemainingFields('', css_class='column-left'),
    )


class Edit(Base, zeit.cms.browser.form.EditForm):
    title = _('Video')


class Display(Base, zeit.cms.browser.form.DisplayForm):
    title = _('Video')
