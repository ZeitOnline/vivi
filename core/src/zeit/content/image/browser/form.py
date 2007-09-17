
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.i18nmessageid

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.content.image.interfaces
import zeit.content.image.image


_ = zope.i18nmessageid.MessageFactory("zope")


class ImageFormBase(object):

    widget_groups = ((u"Bild", zeit.cms.browser.form.REMAINING_FIELDS,
                      "fullWidth"), )

class AddForm(ImageFormBase, zeit.cms.browser.form.AddForm):

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

    form_fields = zope.formlib.form.Fields(
        zeit.content.image.interfaces.IImageSchema,
        render_context=True, omit_readonly=False)

    @zope.formlib.form.action(_("Apply"),
                              condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if not data['data']:
            # in case the (image) data is empty, do not change it.
            del data['data']
        super(EditForm, self).handle_edit_action.success(data)
