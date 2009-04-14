# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson


class UpdateOrder(object):

    def __call__(self, keys):
        # XXX make a decorator
        keys = cjson.decode(keys)
        self.context.updateOrder(keys)
