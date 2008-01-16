# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

from datetime import datetime, timedelta
import pytz
import magic
import libxml2
import libxslt
import re

from pprint import pprint


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
mylog = open('/tmp/content-migration-log','a')


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


    start_id = u"http://xml.zeit.de/"

    setup_infrastructure()

    connector = zeit.connector.connector.Connector(
        {'default': connector_url})

    
    hexer = magic.open(magic.MAGIC_NONE)
    hexer.load()

    do_migration_walk(start_id,connector,hexer)


def do_migration_walk(connector_url,connector,hexer):


    for name, unique_id in connector.listCollection(connector_url):
        res = connector[unique_id]
        print res.type, " ", unique_id
        
        if res.type == 'collection':
            do_migration_walk(unique_id,connector,hexer)


        if re.search(unique_id,'~'):
            continue

        if res.type == 'unknown':
            rtype = guess_content_type(unique_id,res,hexer)
            #print "IS A ", rtype, "\n"
 
            if rtype != 'unknown':

                try:
                    token = connector.lock(unique_id, 'http://xml.zeit.de/users/frodo', datetime.now(pytz.UTC) + timedelta(hours=2))
                
                    res.type = rtype
                    try:
                        connector[unique_id] = res
                    except:
                        traceback.print_exc(file=mylog)
                    connector.unlock(unique_id)
                except:
                    mylog.write("LOCKED")
                    mylog.write(unique_id)
                    mylog.write('\n')
                    #print "LOCK Error"

            
    

    
def guess_content_type(mid,res,hexer):

    rtype = "unknown"

    if not(res.data):
        return rtype
    
    content = res.data.read()
    mt = hexer.buffer(content)

    # print mt

    if re.search('PDF',mt):
        rtype = 'file'
    if re.search('Microsoft Office Document',mt):
        rtype = 'file'
    if re.search('MPEG',mt):
        rtype = 'file'
    if re.search('mp3',mid):
        rtype = 'file'
    
    
    if mt == "XML document text":
        rtype = 'xml'
        try:
            doc = libxml2.parseDoc(content)
            matcher = doc.xpathNewContext()
        
            rootNode = doc.getRootElement()
            root_name = "" + rootNode.name
            #print root_name


            # check article
            if root_name  == 'article':
                rtype = 'article'

            # old channels
            if root_name == 'container':
                rtype = 'channel-simple'

                # eine infobox?
                box = matcher.xpathEval("//container[@layout='artbox' and @label='info']")
                if len(box) > 0:
                    rtype = 'infobox'
                # eine portraitbox
                pbox = matcher.xpathEval("//container[@layout='artbox' and @label='portrait']")
                if len(pbox) > 0:
                    rtype = 'portaitbox'
                
            # check cp + channel
            if root_name == 'centerpage':
                rtype = 'centerpage'
                channel = matcher.xpathEval("//body/container[@layout='channel']")
                if len(channel) > 0:
                    rtype = 'channel'

                container = matcher.xpathEval("//body/container[@layout='container']")
                if len(channel) > 0:
                    rtype = 'container'



            pi = matcher.xpathEval('/processing-instruction()')


            # check gallery
            if len(pi) > 0:
                pi = pi[0]
                #print pi, repr(pi), pi.content

                match = re.search('gallery',pi.content)
                if match:
                    if root_name == 'centerpage':
                        rtype = "gallery"
                    if root_name == 'article':
                        rtype = "gallery-old"
                #if len(match) > 0:
                #    print match[0] 
        




            matcher.xpathFreeContext()
            doc.freeDoc()
            
        except libxml2.parserError:
            mylog.write(mid)
            mylog.write(" Broken XML\n")
            
    if rtype == 'unknown':
        mylog.write("UNKNOWN ")
        mylog.write(mid)
        mylog.write("\n")
    return rtype

    
        




