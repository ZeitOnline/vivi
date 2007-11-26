# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import urllib2

import zope.component

import zc.sourcefactory.basic
import gocept.lxml.objectify
import gocept.cache.method

import zeit.cms.config
import zeit.cms.interfaces


class SimpleXMLSource(zc.sourcefactory.basic.BasicSourceFactory):

    @gocept.cache.method.Memoize(3600)
    def getValues(self):
        request = urllib2.urlopen(self.url)
        xml = gocept.lxml.objectify.fromfile(request)
        return [unicode(serie) for serie in xml.iterchildren()]


class PrintRessortSource(SimpleXMLSource):

    url = zeit.cms.config.PRINT_RESSORT_URL


class NavigationSource(SimpleXMLSource):

    url = zeit.cms.config.RESSORT_URL


class SerieSource(SimpleXMLSource):

    url = zeit.cms.config.SERIE_URL


class CMSContentTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return (interface for name, interface in
                zope.component.getUtilitiesFor(
                    zeit.cms.interfaces.ICMSContentType))
