# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component
import zope.interface

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



class FormBase(object):

    form_fields = zope.formlib.form.fields(
        zeit.cms.content.interfaces.ITemplate)


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _("Add template")
    factory = zeit.cms.content.template.Template
    next_view = 'index.html'

    def suggestName(self, object):
        return object.title


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit template")
