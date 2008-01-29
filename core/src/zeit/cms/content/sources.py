# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import urllib2

import zope.component
import zope.app.appsetup.product

import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import gocept.lxml.objectify
import gocept.cache.method

import zeit.cms.interfaces


logger = logging.getLogger('zeit.cms.content.sources')


class SimpleXMLSource(zc.sourcefactory.basic.BasicSourceFactory):

    @gocept.cache.method.Memoize(3600)
    def getValues(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        url = cms_config[self.config_url]
        logger.debug('Getting %s' % url)
        request = urllib2.urlopen(url)
        xml = gocept.lxml.objectify.fromfile(request)
        return [unicode(serie) for serie in xml.iterchildren()]


class PrintRessortSource(SimpleXMLSource):

    config_url = 'source-print-ressort'


class NavigationSource(SimpleXMLSource):

    config_url = 'source-ressort'


class SerieSource(SimpleXMLSource):

    config_url = 'source-serie'


class CMSContentTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return (interface for name, interface in
                zope.component.getUtilitiesFor(
                    zeit.cms.interfaces.ICMSContentType))
