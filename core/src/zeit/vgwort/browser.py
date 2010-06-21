# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.vgwort.interfaces
import zope.component


class AvailableTokens(object):

    def __call__(self):
        tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        return str(len(tokens))
