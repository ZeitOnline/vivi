from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import zeit.cms.browser.form
import zeit.cms.settings.interfaces
import zeit.content.article.article
import zeit.edit.interfaces
import zope.component
import zope.formlib.form


class Add(zeit.cms.browser.form.AddForm,
          zeit.cms.browser.form.CharlimitMixin):

    factory = zeit.content.article.article.Article
    next_view = 'do-publish'

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticle).select(
            'ressort', 'sub_ressort', 'title', '__name__')

    def setUpWidgets(self, *args, **kw):
        super(Add, self).setUpWidgets(*args, **kw)
        self.set_charlimit('title')

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
        image_factory = zope.component.getAdapter(
            IEditableBody(article), zeit.edit.interfaces.IElementFactory,
            name='image')
        image_factory()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))

        return article

    def add(self, object, container=None):
        super(Add, self).add(object, container)
        self._created_object = ICheckinManager(
            self._created_object).checkin()
        self._checked_out = False

        IPublishInfo(self._created_object).urgent = True
