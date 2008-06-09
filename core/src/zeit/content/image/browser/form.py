
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.i18nmessageid

import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _


_zope = zope.i18nmessageid.MessageFactory("zope")


class ImageFormBase(object):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Image data"), ('__name__', 'data', 'contentType', 'expires'),
            css_class='column-left image-form'),
        gocept.form.grouped.RemainingFields(
            _("Texts"),
            css_class='column-right image-form wide-widgets'),
    )

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImage) +
        zope.formlib.form.FormFields(
            zeit.content.image.interfaces.IImageMetadata)).omit('contentType')


class AddForm(ImageFormBase, zeit.cms.browser.form.AddForm):

    title = _("Add image")

    factory = zeit.content.image.image.Image

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request and 'form.actions.add' not in self.request:
            form = self.request.form
            form['form.expires'] = (
                datetime.date.today() + datetime.timedelta(days=7)).strftime(
                    '%Y-%m-%d 00:00:00')
        super(AddForm, self).setUpWidgets(ignore_request)

    def validate(self, action, data):
        if (not self.request.form.get('form.__name__') and
            self.request.form.get('form.data')):
            self.request.form['form.__name__'] = (
                self.request.form['form.data'].filename)
        return super(AddForm, self).validate(action, data)


class EditForm(ImageFormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit image")
    form_fields = ImageFormBase.form_fields.omit('__name__')

    @zope.formlib.form.action(_zope("Apply"),
                              condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if not data['data']:
            # in case the (image) data is empty, do not change it.
            del data['data']
        super(EditForm, self).handle_edit_action.success(data)


zeit.cms.content.browser.form.AssetBase.add_asset_interface(
    zeit.content.image.interfaces.IImages)
