# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zope.proxy
import lxml.etree
import SilverCity.XML
import StringIO

form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('xml.edit-contents.pt'),
    zope.formlib.interfaces.IPageForm)


class Display(zeit.cms.browser.view.Base):

    @property
    def css_class(self):
        return 'xml-block'

    def update(self):
        content = zope.proxy.removeAllProxies(self.context.xml)
        content = lxml.etree.tostring(content, pretty_print=True,
                                      encoding=unicode)
        io = StringIO.StringIO()
        SilverCity.XML.XMLHTMLGenerator().generate_html(
            io, content.encode('UTF-8'))
        self.xml = io.getvalue().decode('UTF-8')


class EditProperties(zeit.cms.browser.sourceedit.XMLEditForm):

    template = zope.formlib.namedtemplate.NamedTemplate('xmledit_form')

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IXMLBlock).select('xml')
