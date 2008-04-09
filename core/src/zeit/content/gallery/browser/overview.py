# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property
import zope.component

import zeit.cms.content.interfaces
import zeit.wysiwyg.interfaces


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


class Synchronise(object):

    def update(self):
        self.context.reload_image_folder()

    def render(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        self.request.response.redirect('%s/@@overview.html' % url)
        return''
