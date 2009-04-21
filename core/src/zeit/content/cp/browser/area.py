# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import zope.event
import zope.lifecycleevent


class UpdateOrder(object):

    def __call__(self, keys):
        # XXX make a decorator
        keys = cjson.decode(keys)
        self.context.updateOrder(keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))
