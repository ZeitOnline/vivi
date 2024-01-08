import gocept.form.grouped
import zope.cachedescriptors.property
import zope.component

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.content.article.interfaces
import zeit.content.article.recension
import zeit.edit.browser.form
import zeit.edit.browser.view


class RecensionForms(zeit.edit.browser.form.FoldableFormGroup):
    """Article recension forms."""

    title = _('Recensions')

    def render(self):
        if not zeit.cms.checkout.interfaces.ILocalContent.providedBy(self.context):
            return ''
        return super().render()


class Overview(zeit.cms.browser.view.Base):
    """Overview of book information items."""

    title = ''

    @zope.cachedescriptors.property.Lazy
    def recensions(self):
        for recension in self.container:
            url = zope.component.getMultiAdapter((recension, self.request), name='absolute_url')()
            authors = ' '.join(recension.authors)
            yield {'recension': recension, 'authors': authors, 'url': url}

    @zope.cachedescriptors.property.Lazy
    def has_recensions(self):
        return len(self.container) > 0

    @zope.cachedescriptors.property.Lazy
    def container(self):
        return zeit.content.article.interfaces.IBookRecensionContainer(self.context)


class FormBase:
    form_fields = zope.formlib.form.FormFields(zeit.content.article.interfaces.IBookRecension)

    field_groups = (
        gocept.form.grouped.Fields(
            _('Book details'),
            (
                'title',
                'info',
                'authors',
            ),
            css_class='column-left wide-widgets',
        ),
        gocept.form.grouped.Fields(
            _('Publisher'),
            (
                'publisher',
                'location',
                'year',
            ),
            css_class='column-right',
        ),
        gocept.form.grouped.Fields(
            _('misc.'),
            (
                'genre',
                'category',
                'pages',
                'price',
                'age_limit',
                'media_type',
            ),
            css_class='column-left',
        ),
        gocept.form.grouped.Fields(
            _('Translation'), ('original_language', 'translator'), css_class='column-right'
        ),
    )


class Edit(FormBase, zeit.edit.browser.view.EditBox):
    title = _('Edit book information')
    field_groups = FormBase.field_groups + (
        gocept.form.grouped.RemainingFields(_('Raw data'), css_class='fullWidth'),
    )


class Remove(zeit.edit.browser.view.Action):
    def update(self):
        # reload editor to prevent attempt at reloading deleted recension
        self.signal(None, 'reload-editor')
        self.context.__parent__.remove(self.context.__name__)


class Add(FormBase, zeit.edit.browser.view.AddBox):
    title = _('Add book information')
    form_fields = FormBase.form_fields.omit('raw_data')
    factory = zeit.content.article.recension.BookRecension

    def add(self, obj):
        self.context.append(obj)
        # prevent redirect
        self._finished_add = False
        return obj
