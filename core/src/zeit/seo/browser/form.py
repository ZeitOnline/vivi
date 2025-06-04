import gocept.form.grouped
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
from zeit.retresco.interfaces import ISkipEnrich
import zeit.cms.browser.form
import zeit.cms.content.interfaces
import zeit.seo.interfaces


class SEOBaseForm:
    form_fields = zope.formlib.form.FormFields(zeit.seo.interfaces.ISEO).omit(
        'crawler_enabled'
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


class EnableCrawlerWidget(zope.formlib.widget.BrowserWidget):
    name = 'form.enable_crawler'
    button_label = _('Enable Crawler')
    target = 'do-enable-crawler'

    field_css_class = 'field fieldname-enable_crawler'
    reversed = True

    label = None
    hint = None
    required = False

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if not self.request.interaction.checkPermission('zeit.seo.EnableCrawler', self.context):
            return ''
        label = self._translate(self.button_label)
        url = zope.traversing.browser.absoluteURL(self.context, self.request)
        return f"""\
            <button id="{self.name}" type="button" class="button"
            onclick="zeit.cms.lightbox_form('{url}/@@{self.target}')"
            >{label}</button>"""


class SEODisplay(SEOBaseForm, zeit.cms.browser.form.DisplayForm):
    title = _('View SEO data')

    form_fields = SEOBaseForm.form_fields + zope.formlib.form.FormFields(
        zeit.seo.interfaces.ISEO
    ).select('crawler_enabled')

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        items = list(self.widget_groups[0]['widgets'].__Widgets_widgets_items__)
        button = EnableCrawlerWidget(self.context, self.request)
        items.append((None, button))
        self.widget_groups[0]['widgets'] = zope.formlib.form.Widgets(items, prefix=self.prefix)


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def edit_view_name(context):
    return 'seo-edit.html'


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'seo-view.html'


class OnlySEOBaseForm:
    form_fields = zope.formlib.form.FormFields(zeit.seo.interfaces.ISEO).omit('crawler_enabled')

    field_groups = (gocept.form.grouped.RemainingFields(_('SEO data'), 'column-left wide-widgets'),)


class OnlySEOEdit(OnlySEOBaseForm, zeit.cms.browser.form.EditForm):
    title = _('Edit OnlySEO data')


class OnlySEODisplay(OnlySEOBaseForm, zeit.cms.browser.form.DisplayForm):
    title = _('View OnlySEO data')
