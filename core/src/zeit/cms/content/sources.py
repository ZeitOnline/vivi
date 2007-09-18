# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urllib2

import zc.sourcefactory.basic
import gocept.lxml.objectify
import gocept.cache.method

import zeit.cms.config

class KeywordSource(zc.sourcefactory.basic.BasicSourceFactory):
    """Get valid classifications from connector."""

    def getValues(self):
        return iter([u'Deutschland', u'International'])



class NavigationSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return iter([u'Finanzen', u'Deutschland'])


class SerieSource(zc.sourcefactory.basic.BasicSourceFactory):

    url = zeit.cms.config.SERIE_URL

    @gocept.cache.method.Memoize(3600)
    def getValues(self):
        request = urllib2.urlopen(self.url)
        xml = gocept.lxml.objectify.fromfile(request)
        return [unicode(serie) for serie in xml.iterchildren()]
