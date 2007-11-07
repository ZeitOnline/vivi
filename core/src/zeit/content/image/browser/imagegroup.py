# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form
import zeit.cms.browser.form

import zeit.content.image.interfaces
import zeit.content.image.imagegroup


class AddForm(zeit.cms.browser.form.AddForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.image.interfaces.IImageGroup).omit('uniqueId')

    def create(self, data):
        return zeit.content.image.imagegroup.ImageGroup(**data)


class EditForm(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.image.interfaces.IImageGroup,
        render_context=True, omit_readonly=False).omit('uniqueId')
