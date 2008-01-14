# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component


class Overview(object):

    def update(self):
        if 'form.actions.save_sorting' in self.request:
            self.context.updateOrder(self.request.get('images'))


class Synchronise(object):

    def update(self):
        self.context.reload_image_folder()

    def render(self):
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        self.request.response.redirect('%s/@@overview.html' % url)
        return''
