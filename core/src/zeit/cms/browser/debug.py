# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""CMS debug views."""

import sys

class Refcount(object):

    def refcount(self, amount=None):
        # return class reference info
        count = {}
        for module in sys.modules.values():
            for symbol in dir(module):
                ob = getattr(module, symbol)
                if type(ob) == type(object):
                    count[ob] = sys.getrefcount(ob)

        pairs = []
        for ob, v in count.items():
            if hasattr(ob, '__module__'):
                name='%s.%s' % (ob.__module__, ob.__name__)
            else:
                name='%s' % ob.__name__
            pairs.append((v, name))
        pairs.sort()
        pairs.reverse()
        if amount is not None:
            pairs = pairs[:amount]
        return (dict(name=pair[1], count=pair[0]) for pair in pairs)
