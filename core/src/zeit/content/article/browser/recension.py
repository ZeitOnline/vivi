# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.browser.view
from zeit.cms.i18n import MessageFactory as _

import zeit.content.article.interfaces
import zeit.content.article.recension


class Overview(zeit.cms.browser.view.Base):
    """Overview of book information items."""

    title = _('Recensions')

    @zope.cachedescriptors.property.Lazy
    def recensions(self):
        return list(self.container)

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
