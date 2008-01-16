# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zope.formlib.namedtemplate
import zope.formlib.interfaces

import zeit.cms.interfaces


form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('sourceedit.pt'),
    zope.formlib.interfaces.IPageForm)


class TextEditForm(zope.formlib.form.EditForm):
    """Edit form allowing source editing."""

    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')

    form_fields = zope.formlib.form.Fields(
        zeit.cms.content.interfaces.ITextContent).select('data')


class XMLEditForm(zope.formlib.form.EditForm):
    """Edit form allowing source editing."""

    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')
    title = 'Quelltext'

    form_fields = zope.formlib.form.Fields(
        zeit.cms.content.interfaces.IXMLContent).select('xml')
