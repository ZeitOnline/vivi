# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.interface

import zc.table.column
import zc.table.table

import zeit.cms.content.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _


class Manager(object):

    title = _("Templates")

    @zope.cachedescriptors.property.Lazy
    def template_managers(self):
        result = []
        for name, utility in sorted(zope.component.getUtilitiesFor(
            zeit.cms.content.interfaces.ITemplateManager)):
            result.append(dict(
                name=name,
                manager=utility))
        return result



class Listing(zeit.cms.browser.listing.Listing):

    title = _("Templates")
    filter_interface = zope.interface.Interface
    css_class = 'contentListing'

    columns = (
        zc.table.column.SelectionColumn(
            idgetter=lambda item: item.__name__),
        zc.table.column.GetterColumn(
            _('Title'),
            getter=lambda i, f: i.title),
    )

    @property
    def content(self):
        return self.context.values()


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ITemplate).select('title', 'xml')


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _("Add template")
    factory = zeit.cms.content.template.Template
    next_view = 'webdav-properties.html'

    def suggestName(self, object):
        return object.title


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit template")


class Properties(object):

    title = _("Edit webdav properties")

    def update(self):
        if 'dav.save' in self.request:
            data = zip(self.request['name'], self.request['namespace'],
                       self.request['value'])
            new_properties = dict(
                ((item[0], item[1]), item[2])
                for item in data
                if item[0] and item[1])
            properties = zeit.connector.interfaces.IWebDAVWriteProperties(
                self.context)
            properties.update(new_properties)


    @property
    def content(self):
        properties = zeit.connector.interfaces.IWebDAVReadProperties(
            self.context)
        return [
            dict(namespace=item[0][1],
                 name=item[0][0],
                 value=item[1])
            for item in properties.items()]
