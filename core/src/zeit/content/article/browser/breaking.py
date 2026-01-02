import gocept.form.grouped
import zope.component
import zope.formlib.form
import zope.i18n
import zope.interface
import zope.schema

from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IBreakingNewsBody
import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.settings.interfaces
import zeit.content.article.article
import zeit.edit.interfaces
import zeit.push.interfaces


class IPushServices(zope.interface.Interface):
    mobile = zope.schema.Bool(title=_('breaking-news-mobile'), required=False, default=True)
    homepage = zope.schema.Bool(title=_('breaking-news-homepage'), required=False, default=True)


class Add(zeit.cms.browser.form.AddForm, zeit.cms.browser.form.CharlimitMixin):
    factory = zeit.content.article.article.Article
    next_view = 'do-publish'

    form_fields = (
        zope.formlib.form.FormFields(zeit.content.article.interfaces.IArticle).select(
            '__name__',
            'ressort',
            'sub_ressort',
            'channels',
            'commentsAllowed',
            'commentsPremoderate',
        )
        + zope.formlib.form.FormFields(zeit.content.article.interfaces.IBreakingNews).select(
            'title'
        )
        + zope.formlib.form.FormFields(zeit.content.article.edit.interfaces.IBreakingNewsBody)
        + zope.formlib.form.FormFields(IPushServices)
    )

    field_groups = (
        gocept.form.grouped.Fields(
            '',
            (
                'title',
                '__name__',
                'text',
                'breaking_news_image',
                'commentsAllowed',
                'commentsPremoderate',
                'homepage',
                'mobile',
            ),
            css_class='wide-widgets column-left',
        ),
        gocept.form.grouped.Fields(
            '', ('channels', 'ressort', 'sub_ressort'), css_class='column-right'
        ),
    )

    def setUpWidgets(self, *args, **kw):
        if not FEATURE_TOGGLES.find('breaking_news_fallback_image'):
            self.form_fields = self.form_fields.omit('breaking_news_image')

        GET = self.request.form
        if self.request.method == 'GET' and 'form.ressort' in GET:
            # ressort uses a different term/token implementation
            source = zeit.content.article.interfaces.IBreakingNews['ressort'].source(self.context)
            terms = zope.component.getMultiAdapter(
                (source, self.request), zope.browser.interfaces.ITerms
            )
            ressort = terms.getValue(GET.get('form.ressort'))
            source = (
                zeit.content.article.interfaces.IBreakingNews['channels']
                .value_type.fields[0]
                .source(self.context)
            )
            terms = zope.component.getMultiAdapter(
                (source, self.request), zope.browser.interfaces.ITerms
            )
            # We assume the configuration always contains a channel per ressort
            GET['form.channels.0..combination_00'] = terms.getTerm(ressort).token
            # subchannel and subressort currently use the same token implementation,
            # so we can simply copy over the token.
            GET['form.channels.0..combination_01'] = GET.get('form.sub_ressort')
            GET['form.channels.count'] = '1'

        super().setUpWidgets(*args, **kw)
        self.set_charlimit('title')
        self.widgets['title'].cssClass = 'breakingnews-title'
        self.widgets['__name__'].cssClass = 'breakingnews-filename'
        if not self.widgets['text'].hasInput():
            self.widgets['text'].setRenderedValue(
                zope.i18n.translate(self.form_fields['text'].field.default, context=self.request)
            )
        if FEATURE_TOGGLES.find('breaking_news_fallback_image'):
            self._prefill_breaking_news_image()

    def _prefill_breaking_news_image(self):
        if self.widgets['breaking_news_image'].hasInput():
            return

        default_url = zeit.cms.config.get('zeit.push', 'breaking-news-fallback-image')
        if default_url and (default_image := zeit.cms.interfaces.ICMSContent(default_url, None)):
            self.widgets['breaking_news_image'].setRenderedValue(default_image)

    @zope.formlib.form.action(_('Publish and push'), condition=zope.formlib.form.haveInputWidgets)
    def handle_add(self, action, data):
        self.createAndAdd(data)

    def create(self, data):
        message_config = []
        if data.pop('mobile', False):
            source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
            # XXX hard-coded value
            template = source.find('eilmeldung.json')
            config = {
                'type': 'mobile',
                'enabled': True,
                'variant': 'manual',
                'title': source.getDefaultTitle(template),
                'payload_template': template.__name__,
            }

            if image := data.get('breaking_news_image'):
                config['image'] = image.uniqueId
            message_config.append(config)
        if data.pop('homepage', False):
            message_config.append({'type': 'homepage', 'enabled': True})

        article = super().create(data)
        # XXX Duplicated from .form.AddAndCheckout
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        article.year = settings.default_year
        article.volume = settings.default_volume

        push = zeit.push.interfaces.IPushMessages(article)
        push.short_text = data['title']
        push.message_config = message_config

        body = article.body
        if (
            not FEATURE_TOGGLES.find('breaking_news_fallback_image')
            or not IBreakingNewsBody(article).breaking_news_image
        ):
            body.create_item('image')
            if len(body) == 2:
                # The business rule is that each article should start with an image
                # block. Now IBreakingNewsBody caused a paragraph to be created
                # (which already happened in super), but since factories only
                # append at the end, we need to swap the blocks.
                body.updateOrder(tuple(reversed(body.keys())))

        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))

        return article

    def add(self, object, container=None):
        super().add(object, container)
        zeit.content.article.interfaces.IBreakingNews(self._created_object).is_breaking = True
        # We need to check out the new article so that AfterCheckout events are
        # run (which e.g. set default values of ICommonMetadata fields), but
        # the user won't want to edit anything right now, so we check in
        # immediately (and redirect to a view that triggers publishing).
        self._created_object = ICheckinManager(self._created_object).checkin(will_publish_soon=True)
        self._checked_out = False

        IPublishInfo(self._created_object).urgent = True


class Retract:
    @property
    def breakingnews(self):
        return zeit.content.article.interfaces.IBreakingNews(self.context)

    @property
    def is_breaking(self):
        return self.breakingnews.is_breaking

    @property
    def banner_published(self):
        return IPublishInfo(self.banner).published

    @property
    def banner_matches(self):
        return self.breakingnews.banner_matches()

    @property
    def banner(self):
        banner = zope.component.getUtility(zeit.push.interfaces.IBanner)
        return banner.xml_banner
