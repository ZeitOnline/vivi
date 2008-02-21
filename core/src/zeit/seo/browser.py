# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

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


class SEOEdit(SEOBaseForm, zeit.cms.browser.form.EditForm):

    title = _('Edit SEO data')


class SEODisplay(SEOBaseForm, zeit.cms.browser.form.DisplayForm):

    title = _('View SEO data')
