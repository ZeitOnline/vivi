from zeit.cms.checkout.interfaces import ILocalContent
from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import uuid
import zeit.cms.browser.form
import zeit.cms.clipboard.interfaces
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.cms.settings.interfaces
import zeit.content.article.interfaces
import zeit.edit.interfaces
import zeit.wysiwyg.interfaces
import zope.browser.interfaces
import zope.event
import zope.formlib.form
import zope.lifecycleevent


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class ArticleFormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata,
        zeit.cms.interfaces.ICMSContent).omit('textLength',
                                              'has_recensions')

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        base.text_fields,
        gocept.form.grouped.RemainingFields(
            _('misc.'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Options"),
            base.option_fields.fields + (
                'has_recensions', 'artbox_thema'),
            css_class='column-right checkboxes'))


class AddAndCheckout(zeit.cms.browser.view.Base):

    def __call__(self):
        article = self.get_article()
        name = '{0}.tmp'.format(uuid.uuid4())
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            article).renameable = True
        self.context[name] = article
        self.redirect(self.url(self.context[name], '@@checkout'))

    def get_article(self):
        article = zeit.content.article.article.Article()
        settings = zeit.cms.settings.interfaces.IGlobalSettings(
            self.context)
        article.year = settings.default_year
        article.volume = settings.default_volume
        article.ressort = self._get_source_value(article, 'ressort')
        article.sub_ressort = self._get_source_value(article, 'sub_ressort')
        article.genre = self._get_source_value(article, 'genre')
        article.authorships = self._create_authorship(article)
        if article.ressort:
            article.channels = ((article.ressort, article.sub_ressort),)
        article.body.create_item('image')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(article))
        return article

    def _create_authorship(self, article):
        value = self.request.form.get('form.authorships')
        author = None
        if not value:
            return ()
        from_clipboard = self._author_from_clipboard(value)
        if from_clipboard is not None:
            author = from_clipboard
        else:
            author = self._author_adapted_from_value(value)
        if author is None:
            return ()
        return [article.authorships.create(author)]

    def _author_from_clipboard(self, value):
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(
            self.request.principal)
        entry = clipboard.get(value)
        if entry is None:
            return
        if len(entry.items()) != 1:
            return
        if not zeit.content.author.interfaces.IAuthor.providedBy(
                entry.items()[0][1].references):
            return
        return entry.items()[0][1].references

    def _author_adapted_from_value(self, value):
        try:
            return zeit.cms.interfaces.ICMSContent(value)
        except TypeError:
            return

    def _get_source_value(self, article, fieldname):
        token = self.request.form.get('form.%s' % fieldname)
        source = zeit.content.article.interfaces.IArticle[fieldname].source
        source = source(article)
        if not token:
            return
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)
        return terms.getValue(token)


class EditForm(ArticleFormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit article')


class DisplayForm(ArticleFormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View article metadata')


class WYSIWYGEdit(zeit.cms.browser.form.EditForm):
    """Edit article content using wysiwyg editor."""

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticleMetadata).select(
                'supertitle', 'title', 'byline', 'subtitle') +
        zope.formlib.form.FormFields(
            zeit.wysiwyg.interfaces.IHTMLContent))

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Content'),
            css_class='full-width wide-widgets'),)


class DispatchToViewOrEdit(zeit.cms.browser.view.Base):

    def __call__(self):
        in_repository = not ILocalContent.providedBy(self.context)
        existing_checkout = self._find_checked_out()
        if in_repository and existing_checkout:
            self.redirect(self.url(existing_checkout))
        else:
            view = zope.component.getMultiAdapter(
                (self.context, self.request), name='edit.html')
            return view()

    def _find_checked_out(self):
        for item in zeit.cms.checkout.interfaces.IWorkingcopy(None).values():
            if not zeit.cms.interfaces.ICMSContent.providedBy(item):
                continue
            if item.uniqueId == self.context.uniqueId:
                return item
