# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zeit.cms.browser.form

import zeit.content.image.interfaces
import zeit.content.image.imagegroup


class FormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImageGroup) +
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImageMetadata))



class AddForm(FormBase, zeit.cms.browser.form.AddForm):

    factory = zeit.content.image.imagegroup.ImageGroup
    checkout = False


class EditForm(FormBase, zeit.cms.browser.form.EditForm):

    form_fields = FormBase.form_fields.omit('__name__')
