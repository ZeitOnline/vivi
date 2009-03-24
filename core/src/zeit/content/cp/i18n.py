# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.i18n

class Dummy(object):
    pass

MessageFactory = zope.i18n.MessageFactory(Dummy.__module__)
