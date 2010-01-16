# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.pagetemplate
import zope.formlib.form

import zeit.cms.browser.menu
import zeit.cms.checkout.helper
import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    title = _('Bulk change image copyright')


class Form(zeit.cms.browser.lightbox.Form):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImageMetadata).select('copyrights')

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'copyright.pt')

    def get_data(self):
        # We don't have any initial data.
        return {}

    @zope.formlib.form.action(_('Set copyrights'))
    def action_set_copyrights(self, action, data):
        changed = []
        for name in self.context:
            obj = self.context[name]
            metadata = zeit.content.image.interfaces.IImageMetadata(
                obj, None)
            if metadata is None:
                continue
            zeit.cms.checkout.helper.with_checked_out(
                obj, lambda x: self.set_copyrights(x, data['copyrights']))
            changed.append(name)

        self.send_message(
            _('Copyright changed for: ${changes}',
              mapping=dict(changes=', '.join(changed))))


    @staticmethod
    def set_copyrights(obj, copyrights):
        metadata = zeit.content.image.interfaces.IImageMetadata(obj)
        metadata.copyrights = copyrights
        return obj
