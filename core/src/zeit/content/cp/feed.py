# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import md5
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.xmlsupport
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.content.cp.interfaces
import zope.app.appsetup.product
import zope.component
import zope.interface

class Feed(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.cp.interfaces.IFeed)

    default_template = '<foo />'

    @classmethod
    def get_feed(cls, url):
        hash_ = md5.new(url).hexdigest()
        rss_folder = get_rss_folder() # XXX: use adapters?! instead
        try:
            return rss_folder[hash_]
        except KeyError:
            feed = cls()
            feed.url = url
            feed = rss_folder[hash_] = feed
            return feed


feedFactory = zeit.cms.content.adapter.xmlContentFactory(Feed)

resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory('feed')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.IFeed)(resourceFactory)

def get_rss_folder():
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    rss_folder_name = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')['rss-folder']
    try:
        return repository[rss_folder_name]
    except KeyError:
        repository[rss_folder_name] = zeit.cms.repository.folder.Folder()
        return repository[rss_folder_name]

