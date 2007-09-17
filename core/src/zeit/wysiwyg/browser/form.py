# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.wysiwyg.interfaces


class EditForm(zope.formlib.form.EditForm):

    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')

    form_fields = zope.formlib.form.Fields(
        zeit.wysiwyg.interfaces.IHTMLContent,
        render_context=True)
