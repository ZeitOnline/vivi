# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.cachedescriptors.property
import zope.component

import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.wysiwyg.interfaces
from zeit.cms.i18n import MessageFactory as _


class Overview(object):

    def update(self):
        if 'form.actions.save_sorting' in self.request:
            self.context.updateOrder(self.request.get('images'))

    def get_text(self, entry):
        return zeit.wysiwyg.interfaces.IHTMLConverter(entry).to_html(
            entry.text)

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context)


class Synchronise(zeit.cms.browser.view.Base):

    def __call__(self):
        self.context.reload_image_folder()
        self.send_message(_('Image folder was synchronised.'))
        self.redirect(self.url('@@overview.html'))
        return''
