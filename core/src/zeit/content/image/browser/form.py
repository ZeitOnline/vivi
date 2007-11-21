
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.i18nmessageid

import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image

from zeit.cms.i18n import MessageFactory as _


_zope = zope.i18nmessageid.MessageFactory("zope")


class ImageFormBase(object):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Image data"), ('__name__', 'data', 'contentType', 'expires'),
            css_class='column-left image-form'),
        gocept.form.grouped.RemainingFields(
            _("Texts"),
            css_class='column-right image-form'),
    )

class AddForm(ImageFormBase, zeit.cms.browser.form.AddForm):

    title = _("Add image")

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.image.interfaces.IImageSchema,
            omit_readonly=False))

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            form = self.request.form
            if not form:
                form['form.year'] = str(datetime.datetime.now().year)
                form['form.volume'] = str(int(  # Strip leading 0
                    datetime.datetime.now().strftime('%W')))
        super(AddForm, self).setUpWidgets(ignore_request)

    def create(self, data):
        return zeit.content.image.image.Image(**data)


class EditForm(ImageFormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit image")
    form_fields = zope.formlib.form.Fields(
        zeit.content.image.interfaces.IImageSchema,
        render_context=True, omit_readonly=False)

    @zope.formlib.form.action(_zope("Apply"),
                              condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if not data['data']:
            # in case the (image) data is empty, do not change it.
            del data['data']
        super(EditForm, self).handle_edit_action.success(data)
