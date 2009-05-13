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
import zeit.cms.content.property
import feedparser
import lxml.etree

CHANNEL_MAPPING = {'title': 'title',
                   'subtitle': 'description',
                   'link': 'link'}
ITEM_MAPPING = {'title': 'title',
                'description': 'description',
                'link': 'link'}


class Feed(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.cp.interfaces.IFeed)

    default_template = """\
<feed xmlns:py="http://codespeak.net/lxml/objectify/pytype" />"""

    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url')

    def fetch_and_convert(self):
        if self.xml.get('error'):
            del self.xml.attrib['error']
        if self.xml.getchildren():
            self.xml.remove(self.xml.rss)
        rss = lxml.etree.Element('rss')
        rss.set('version', '2.0')
        src = feedparser.parse(self.url)
        if src.bozo:
            exc = src.bozo_exception
            self.xml.set('error', '%s: %s' % (type(exc), str(exc)))
            return
        channel = lxml.etree.Element('channel')
        for src_key, rss_key in CHANNEL_MAPPING.items():
            elem = lxml.etree.Element(rss_key)
            elem.text = src.feed[src_key]
            channel.append(elem)
        for entry in src.entries:
            item = lxml.etree.Element('item')
            for src_key, rss_key in ITEM_MAPPING.items():
                elem = lxml.etree.Element(rss_key)
                elem.text = entry[src_key]
                item.append(elem)
            channel.append(item)
        rss.append(channel)
        self.xml.append(rss)



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
            feed.fetch_and_convert() # XXX async?!
            feed = self.folder[hash_] = feed
            return feed
