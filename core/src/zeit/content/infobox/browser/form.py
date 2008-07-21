# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import gocept.form.grouped
import zc.form.browser.combinationwidget
import zope.app.appsetup.interfaces
import zope.app.form.browser
import zope.cachedescriptors.property
import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.wysiwyg.browser.widget
from zeit.cms.i18n import MessageFactory as _

import zeit.content.infobox.interfaces
import zeit.content.infobox.infobox


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.infobox.interfaces.IInfobox) +
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent))

    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'contents',),
            css_class='column-left wide-widgets'),
        gocept.form.grouped.RemainingFields(
            _('Head'),
            css_class='column-right'))


class ContentWidget(zc.form.browser.combinationwidget.CombinationWidget):

    @zope.cachedescriptors.property.Lazy
    def widgets(self):
        field = self.context
        res = []
        assert len(field.fields) == 2
        for nr, f in enumerate(field.fields):
            f = f.bind(self.context)
            if nr == 0:  # Text
                w = zope.component.getMultiAdapter((f, self.request,),
                                                   self.widget_interface)
            else:
                w = zeit.wysiwyg.browser.widget.FckEditorWidget(
                    f, self.request)
            w.setPrefix(self.name + ".")
            res.append(w)
        return res


class Add(FormBase, zeit.cms.browser.form.AddForm):

    factory = zeit.content.infobox.infobox.Infobox
    title = _('Add infobox')
    #form_fields['contents'].custom_widget = ContentWidget


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit infobox')
    form_fields = FormBase.form_fields.omit('__name__')
    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            ('supertitle', 'contents',),
            css_class='full-width wide-widgets'),
    )

    form_fields['contents'].custom_widget = lambda context, request: (
        zope.app.form.browser.TupleSequenceWidget(
            context, zeit.content.infobox.interfaces.IInfobox['contents'],
            request, subwidget=ContentWidget))



class Display(FormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View infobox')


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register_asset_interface(event):
    zeit.cms.content.browser.form.AssetBase.add_asset_interface(
        zeit.content.infobox.interfaces.IInfoboxReference)
