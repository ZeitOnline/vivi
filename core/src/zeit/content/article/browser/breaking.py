from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublishInfo
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.settings.interfaces
import zeit.content.article.article
import zeit.edit.interfaces
import zeit.push.interfaces
import zope.formlib.form
import zope.i18n
import zope.interface
import zope.schema


class IPushServices(zope.interface.Interface):

    mobile = zope.schema.Bool(
        title=_('breaking-news-mobile'), required=False, default=True)
    homepage = zope.schema.Bool(
        title=_('breaking-news-homepage'), required=False, default=True)
    social = zope.schema.Bool(
        title=_('breaking-news-social'), required=False, default=True)


class Add(zeit.cms.browser.form.AddForm,
          zeit.cms.browser.form.CharlimitMixin):

    factory = zeit.content.article.article.Article
    next_view = 'do-publish'

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticle).select(
                '__name__', 'ressort', 'sub_ressort', 'channels',
                'commentsAllowed', 'commentsPremoderate') +
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IBreakingNews).select('title') +
        zope.formlib.form.FormFields(
            zeit.content.article.edit.interfaces.IBreakingNewsBody) +
        zope.formlib.form.FormFields(
            IPushServices)
    )

    field_groups = (
        gocept.form.grouped.Fields('', (
            'title', '__name__', 'text',
            'commentsAllowed', 'commentsPremoderate',
            'homepage', 'mobile', 'social'),
            css_class='wide-widgets column-left'),
        gocept.form.grouped.Fields('', (
            'ressort', 'sub_ressort', 'channels'),
            css_class='column-right'),
    )

    def setUpWidgets(self, *args, **kw):
        if not FEATURE_TOGGLES.find('breakingnews_with_channel'):
            self.form_fields = self.form_fields.omit('channels')
        GET = self.request.form
        GET['form.channels.0..combination_00'] = GET.get('form.ressort')
        GET['form.channels.0..combination_01'] = GET.get('form.sub_ressort')
        GET['form.channels.count'] = '1'
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('title')
        self.widgets['title'].cssClass = 'breakingnews-title'
        self.widgets['__name__'].cssClass = 'breakingnews-filename'
        if not self.widgets['text'].hasInput():
            self.widgets['text'].setRenderedValue(
                zope.i18n.translate(
                    self.form_fields['text'].field.default,
                    context=self.request))

    @zope.formlib.form.action(
        _('Publish and push'), condition=zope.formlib.form.haveInputWidgets)
    def handle_add(self, action, data):
        self.createAndAdd(data)

    def create(self, data):
        message_config = []
        if data.pop('mobile', False):
            source = zeit.push.interfaces.PAYLOAD_TEMPLATE_SOURCE.factory
            # XXX hard-coded value
            template = source.find('eilmeldung.json')
            message_config.append({
                'type': 'mobile', 'enabled': True, 'variant': 'manual',
                'title': source.getDefaultTitle(template),
                'payload_template': template.__name__,
            })
        if data.pop('homepage', False):
            message_config.append(
                {'type': 'homepage', 'enabled': True})
        if data.pop('social', False):
            message_config.append(
                {'type': 'facebook', 'enabled': True,
                 'override_text': data['title'],
                 'account': zeit.push.interfaces.facebookAccountSource(
                     self.context).MAIN_ACCOUNT})
            message_config.append(
                {'type': 'twitter', 'enabled': True,
                 'account': zeit.push.interfaces.twitterAccountSource(
                     self.context).MAIN_ACCOUNT})

        article = super().create(data)
        # XXX Duplicated from .form.AddAndCheckout
        settings = zeit.cms.settings.interfaces.IGlobalSettings(
            self.context)
        article.year = settings.default_year
        article.volume = settings.default_volume

        push = zeit.push.interfaces.IPushMessages(article)
        push.short_text = data['title']
        push.message_config = message_config

        body = article.body
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
        zeit.content.article.interfaces.IBreakingNews(
            self._created_object).is_breaking = True
        # We need to check out the new article so that AfterCheckout events are
        # run (which e.g. set default values of ICommonMetadata fields), but
        # the user won't want to edit anything right now, so we check in
        # immediately (and redirect to a view that triggers publishing).
        self._created_object = ICheckinManager(
            self._created_object).checkin()
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
        banner = zope.component.getUtility(
            zeit.push.interfaces.IBanner)
        return banner.xml_banner
