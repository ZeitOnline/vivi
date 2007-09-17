# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zc.sourcefactory.basic


class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Get valid classifications from connector."""

    def getValues(self):
        return iter([u'Deutschland', u'International'])



class NavigationSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return iter([u'Finanzen', u'Deutschland'])


class SerieSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return iter((u"theater", u"Terror"))
