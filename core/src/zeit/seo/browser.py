# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.content.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.seo.interfaces


class SEOBaseForm(object):

    form_fields = (
        zope.formlib.form.FormFields(zeit.seo.interfaces.ISEO) +
        zope.formlib.form.FormFields(
            zeit.cms.content.interfaces.ICommonMetadata).select(
                'keywords', 'ressort', 'sub_ressort', 'serie'))

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('SEO data'),
            'column-left wide-widgets'),
        gocept.form.grouped.Fields(
            _('Standard metadata'),
            ('keywords', 'ressort', 'sub_ressort', 'serie'),
            'column-right'))


class SEOEdit(SEOBaseForm, zeit.cms.browser.form.EditForm):

    title = _('Edit SEO data')


class SEODisplay(SEOBaseForm, zeit.cms.browser.form.DisplayForm):

    title = _('View SEO data')


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def edit_view_name(context):
    return 'seo-edit.html'


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def display_view_name(context):
    return 'seo-view.html'
