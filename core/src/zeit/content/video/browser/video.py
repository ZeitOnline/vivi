import gocept.form.grouped
import zope.dublincore.interfaces
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
        zeit.cms.related.interfaces.IRelatedContent,
        zeit.content.image.interfaces.IImages,
        zeit.cms.workflow.interfaces.IPublishInfo,
        zope.dublincore.interfaces.IDCTimes,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE,
    ).select(
        'supertitle',
        'title',
        'subtitle',
        'teaserText',
        'product',
        'ressort',
        'keywords',
        'serie',
        'banner',
        'banner_id',
        'type',
        'has_recensions',
        'commentsAllowed',
        'commentsPremoderate',
        'related',
        'channels',
        'video_still_copyright',
        'has_advertisement',
        # remaining:
        '__name__',
        'image',
        'created',
        'date_first_released',
        'modified',
        'expires',
        'video_still',
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
                'has_recensions',
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
            _('Video-Thumbnail'), ('image'), css_class='wide-widgets column-left'
        ),
        gocept.form.grouped.RemainingFields('', css_class='column-left'),
    )


class Edit(Base, zeit.cms.browser.form.EditForm):
    title = _('Video')


class Display(Base, zeit.cms.browser.form.DisplayForm):
    title = _('Video')


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
        raise TypeError('No still url')


class PlaylistDisplayForm(zeit.cms.browser.form.DisplayForm):
    title = _('View playlist')

    form_fields = zope.formlib.form.FormFields(zeit.content.video.interfaces.IPlaylist)
