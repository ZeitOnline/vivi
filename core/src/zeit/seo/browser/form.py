import gocept.form.grouped
import grokcore.component as grok
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
from zeit.retresco.interfaces import ISkipEnrich
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.seo.interfaces


class SEOBaseForm:
    form_fields = zope.formlib.form.FormFields(
        zeit.seo.interfaces.ISEO
    ) + zope.formlib.form.FormFields(zeit.cms.content.interfaces.ICommonMetadata).select(
        'keywords', 'ressort', 'sub_ressort', 'serie'
    )

    field_groups = (
        gocept.form.grouped.RemainingFields(_('SEO data'), 'column-left wide-widgets'),
        gocept.form.grouped.Fields(
            _('Standard metadata'),
            ('keywords', 'keyword_entity_type', 'ressort', 'sub_ressort', 'serie'),
            'column-right',
        ),
    )


class SEOEdit(SEOBaseForm, zeit.cms.browser.form.EditForm):
    title = _('Edit SEO data')

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        if 'disable_enrich' in data:
            value = data.pop('disable_enrich')
            content = zope.security.proxy.getObject(self.context)
            if value:
                zope.interface.alsoProvides(content, ISkipEnrich)
            else:
                zope.interface.noLongerProvides(content, ISkipEnrich)
        return super().handle_edit_action.success(data)


class EnableCrawlerAction(zope.formlib.form.Action):
    def __init__(self):
        super().__init__(_('Enable Crawler'), name='enable-crawler', condition=self.has_permission)

    @staticmethod
    def has_permission(form, action):
        return form.request.interaction.checkPermission('zeit.seo.EnableCrawler', form.context)


class RenderEnableCrawlerAction(zeit.cms.browser.form.RenderLightboxAction):
    grok.context(EnableCrawlerAction)
    target = 'do-enable-crawler'


class SEODisplay(SEOBaseForm, zeit.cms.browser.form.DisplayForm):
    title = _('View SEO data')

    extra_actions = zope.formlib.form.Actions()
    extra_actions.append(EnableCrawlerAction())

    @property
    def actions(self):
        return list(super().actions) + list(self.extra_actions)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def edit_view_name(context):
    return 'seo-edit.html'


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'seo-view.html'


class OnlySEOBaseForm:
    form_fields = zope.formlib.form.FormFields(zeit.seo.interfaces.ISEO)

    field_groups = (gocept.form.grouped.RemainingFields(_('SEO data'), 'column-left wide-widgets'),)


class OnlySEOEdit(OnlySEOBaseForm, zeit.cms.browser.form.EditForm):
    title = _('Edit OnlySEO data')


class OnlySEODisplay(OnlySEOBaseForm, zeit.cms.browser.form.DisplayForm):
    title = _('View OnlySEO data')
