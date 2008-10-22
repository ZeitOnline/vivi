# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.browser.view
from zeit.content.article.i18n import MessageFactory as _

import gocept.form.grouped

import zeit.content.article.interfaces
import zeit.content.article.recension


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


class RecensionIndex(object):

    def __call__(self):
        view = zope.component.getMultiAdapter(
            (self.context.__parent__, self.request),
            name='recensions.html')
        return view()


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

class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add book information')
    form_fields = FormBase.form_fields.omit('raw_data')
    factory = zeit.content.article.recension.BookRecension

    def add(self, obj):
        self.context.append(obj)
        self._finished_add = True

    def nextURL(self):
        return zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')()


class Edit(FormBase, zeit.cms.browser.form.EditForm):
    """Edit form."""

    title = _('Edit book information')
    redirect_to_parent_after_edit = True
    field_groups = FormBase.field_groups + (
        gocept.form.grouped.RemainingFields(
            _('Raw data'),
            css_class='fullWidth'),)


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def edit_view_name(context):
    return 'recensions.html'


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'recensions.html'
