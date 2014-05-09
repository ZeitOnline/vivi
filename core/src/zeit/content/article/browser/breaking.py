from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.settings.interfaces
import zeit.content.article.article
import zeit.edit.interfaces
import zeit.push.interfaces
import zope.component
import zope.formlib.form
import zope.i18n


class Add(zeit.cms.browser.form.AddForm,
          zeit.cms.browser.form.CharlimitMixin):

    factory = zeit.content.article.article.Article
    next_view = 'do-publish'

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticle).select(
                'ressort', 'sub_ressort', 'title', '__name__')
        + zope.formlib.form.FormFields(
            zeit.content.article.edit.interfaces.IBreakingNewsBody)
        + zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushServices).select(
                *zeit.push.interfaces.PUSH_SERVICES)
    )

    field_groups = (
        gocept.form.grouped.Fields('', (
            'ressort', 'sub_ressort', 'title', '__name__', 'text')),
        gocept.form.grouped.Fields(
            _('Push services'), zeit.push.interfaces.PUSH_SERVICES),
    )

    def setUpWidgets(self, *args, **kw):
        super(Add, self).setUpWidgets(*args, **kw)
        self.set_charlimit('title')
        self.widgets['title'].cssClass = 'breakingnews-title'
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
        article = super(Add, self).create(data)
        # XXX Duplicated from .form.AddAndCheckout
        settings = zeit.cms.settings.interfaces.IGlobalSettings(
            self.context)
        article.year = settings.default_year
        article.volume = settings.default_volume

        body = IEditableBody(article)
        image_factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory,
            name='image')
        image_factory()
        if len(body) == 2:
            # The business rule is that each article should start with an image
            # block. Now IBreakingNewsBody caused a paragraph to be created
            # (which already happened in super), but since factories only
            # append at the end, we need to swap the blocks.
            body.updateOrder(tuple(reversed(body.keys())))

        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))

        return article

    def add(self, object, container=None):
        super(Add, self).add(object, container)
        # We need to check out the new article so that AfterCheckout events are
        # run (which e.g. set default values of ICommonMetadata fields), but
        # the user won't want to edit anything right now, so we check in
        # immediately (and redirect to a view that triggers publishing).
        self._created_object = ICheckinManager(
            self._created_object).checkin()
        self._checked_out = False

        IPublishInfo(self._created_object).urgent = True
        zeit.push.interfaces.IPushServices(self._created_object).enabled = True
