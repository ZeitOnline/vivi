# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from datetime import datetime, timedelta
import pytz


import zope.interface
import zope.app.component.hooks
import zope.annotation.attribute
import zope.annotation.interfaces
from zope.traversing.interfaces import IContainmentRoot
from zope.app.component.interfaces import ISite

import zeit.connector.cache
import zeit.connector.connector
import zeit.connector.interfaces

RESOURCE_TYPE_PROPERTY = ('type', 'http://namespaces.zeit.de/CMS/meta')

class Site(object):
    zope.interface.implements(
        ISite, IContainmentRoot,
        zope.annotation.interfaces.IAttributeAnnotatable)

    def getSiteManager(self):
        return zope.component.getGlobalSiteManager()


def setup_infrastructure():
    site = Site()
    old_site = zope.app.component.hooks.getSite()
    zope.app.component.hooks.setSite(site)

    site_manager = zope.app.component.hooks.getSiteManager()
    site_manager.registerAdapter(
        zope.annotation.attribute.AttributeAnnotations,
        (zope.annotation.interfaces.IAttributeAnnotatable,),
        zope.annotation.interfaces.IAnnotations)

    site_manager.registerAdapter(
        zeit.connector.cache.resourceCacheFactory,
        (ISite,),
        zeit.connector.interfaces.IResourceCache)


def migrate_content_types(connector_url):
    setup_infrastructure()
    connector = zeit.connector.connector.Connector(
        {'default': connector_url})

    #for name, unique_id in connector.listCollection(u'http://xml.zeit.de/'):
    #    print unique_id
    article_id = u"http://xml.zeit.de/1989/14/test-artikel"
    print article_id

    res = connector[article_id]
    
    print res.properties[RESOURCE_TYPE_PROPERTY]

    token = connector.lock(article_id, 'http://xml.zeit.de/users/frodo', datetime.now(pytz.UTC) + timedelta(hours=2))

    res.properties[RESOURCE_TYPE_PROPERTY] = ("XYZ")

    print res.properties[RESOURCE_TYPE_PROPERTY]
    
    connector[article_id] = res

    connector.unlock(article_id)

    


    
        




