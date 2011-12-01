# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.i18nmessageid
import zope.i18n
import zope.formlib.form
import zope.formlib.namedtemplate
import zope.formlib.interfaces
import zope.publisher.interfaces.browser

import zope.app.pagetemplate

import zeit.xmleditor.interfaces


xml_form_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    zope.app.pagetemplate.ViewPageTemplateFile('form.pt'),
    zope.formlib.interfaces.IPageForm)


@zope.component.adapter(zope.formlib.interfaces.IAction,
                        zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zope.publisher.interfaces.browser.IBrowserView)
def render_button(self, request):
    if not self.available():
        return ''
    label = self.label
    if isinstance(label, zope.i18nmessageid.Message):
        label = zope.i18n.translate(self.label, context=self.form.request)
    return ('<input type="button" id="%s" name="%s" value="%s"'
            ' class="button" />' %
            (self.__name__, self.__name__, label)
            )


class FormBase(zope.formlib.form.EditForm):

    label = 'Bearbeiten'

    template = zope.formlib.namedtemplate.NamedTemplate('xmlform')


class XInclude(FormBase):

    label = 'Include bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.xmleditor.interfaces.IXInclude)


class Block(FormBase):

    label = 'Block bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.xmleditor.interfaces.IBlock)


class Text(FormBase):

    label = 'Text bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.xmleditor.interfaces.IText)


class Raw(FormBase):

    label = 'Raw bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.xmleditor.interfaces.IRaw)
