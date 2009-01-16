# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.sourcefactory.basic

from zeit.cms.i18n import MessageFactory as _


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {u'image-only': _('Image only'),
              u'hidden': _('Hidden'),
             }

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]

