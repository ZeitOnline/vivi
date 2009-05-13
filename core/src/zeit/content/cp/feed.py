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


feedFactory = zeit.cms.content.adapter.xmlContentFactory(Feed)

resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory('feed')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.IFeed)(resourceFactory)


class FeedManager(object):

    zope.interface.implements(
        zeit.content.cp.interfaces.IFeedManager)

    @property
    def folder(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        rss_folder_name = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')['rss-folder']
        try:
            return repository[rss_folder_name]
        except KeyError:
            repository[rss_folder_name] = zeit.cms.repository.folder.Folder()
            return repository[rss_folder_name]

    def get_feed(self, url):
        hash_ = md5.new(url).hexdigest()
        try:
            return self.folder[hash_]
        except KeyError:
            feed = Feed()
            feed.url = url
            feed = self.folder[hash_] = feed
            return feed
