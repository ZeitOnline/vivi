# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.content.article.interfaces
import zeit.content.article.recension
import zope.cachedescriptors.property
import zope.component


class RecensionForms(zeit.edit.browser.form.FormGroup):
    """Article recension forms."""

    title = _('Recensions')


class Overview(zeit.cms.browser.view.Base):
    """Overview of book information items."""

    title = _('Recensions')

    @zope.cachedescriptors.property.Lazy
    def recensions(self):
        for recension in self.container:
            url = zope.component.getMultiAdapter(
                (recension, self.request), name='absolute_url')()
            authors = ' '.join(recension.authors)
            yield dict(publisher=recension.publisher,
                       location=recension.location,
                       year=recension.year,
                       price=recension.price,
                       authors=authors,
                       url=url,
                       title=recension.title)

    @zope.cachedescriptors.property.Lazy
    def has_recensions(self):
        return len(self.container) > 0

    @zope.cachedescriptors.property.Lazy
    def container(self):
        return zeit.content.article.interfaces.IBookRecensionContainer(
            self.context)


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IBookRecension)

    field_groups = (
        gocept.form.grouped.Fields(
            _('Book details'),
            ('title', 'info', 'authors',),
            css_class='column-left wide-widgets'),
        gocept.form.grouped.Fields(
            _('Publisher'),
            ('publisher', 'location', 'year',),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _('misc.'),
            ('genre', 'category', 'pages', 'price',
             'age_limit', 'media_type',),
            css_class='column-left'),
        gocept.form.grouped.Fields(
            _('Translation'),
            ('original_language', 'translator'),
            css_class='column-right'),
        )


class Edit(FormBase, zeit.edit.browser.view.EditBox):

    title = _('Edit book information')
    field_groups = FormBase.field_groups + (
        gocept.form.grouped.RemainingFields(
            _('Raw data'),
            css_class='fullWidth'),)
    undo_description = _('edit recension')


class Add(FormBase, zeit.edit.browser.view.AddBox):

    title = _('Add book information')
    form_fields = FormBase.form_fields.omit('raw_data')
    factory = zeit.content.article.recension.BookRecension
    undo_description = _('add recension')

    def add(self, obj):
        self.context.append(obj)
        # prevent redirect
        self._finished_add = False
        return obj
