# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

class Overview(object):

    def update(self):
        if 'form.actions.save_sorting' in self.request:
            self.context.updateOrder(self.request.get('images'))
