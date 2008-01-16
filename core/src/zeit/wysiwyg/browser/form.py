# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zope.app.pagetemplate.viewpagetemplatefile

import zeit.wysiwyg.interfaces


class EditForm(zope.formlib.form.EditForm):

    template = zope.formlib.namedtemplate.NamedTemplate('sourceedit_form')
    additional_information = (
        zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
            'header.pt'))

    form_fields = zope.formlib.form.Fields(
        zeit.wysiwyg.interfaces.IHTMLContent,
        render_context=True)


    @property
    def metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context)
