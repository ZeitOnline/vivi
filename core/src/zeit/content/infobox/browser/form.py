# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.interfaces
import zeit.cms.browser.form

import zeit.content.infobox.interfaces


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.infobox.interfaces.IInfobox) +
        zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent))


class Add(FormBase, zeit.cms.browser.form.AddForm):

    pass

