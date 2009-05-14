# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import datetime
import feedparser
import lxml.etree
import md5
import pytz
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.content.cp.interfaces
import zope.app.appsetup.product
import zope.component
import zope.interface


def identity(mapping, items):
    mapping.update([(x, x) for x in items])

CHANNEL_MAPPING = {'subtitle': 'description', 'updated': 'pubDate'}
identity(CHANNEL_MAPPING, ['title', 'link', 'language', 'copyright'])

IMAGE_MAPPING = {'href': 'url'}
identity(IMAGE_MAPPING, ['title', 'link', 'width', 'height', 'description'])

ITEM_MAPPING = {'id': 'guid', 'updated': 'pubDate', 'summary': 'description'}
identity(ITEM_MAPPING, ['title', 'link', 'author'])


class Feed(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.cp.interfaces.IFeed)

    default_template = """\
<feed xmlns:py="http://codespeak.net/lxml/objectify/pytype" />"""

    zeit.cms.content.dav.mapProperties(
        zeit.content.cp.interfaces.IFeed,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('url', 'entry_count', 'last_update', 'error'))

    def fetch_and_convert(self):
        """Load and reconvert the feed into RSS 2.

        You should not call `fetch_and_convert` directly. Use the FeedManager
        instead."""

        self.last_update = datetime.datetime.now(pytz.UTC)
        self.parsed = feedparser.parse(self.url)
        if self.parsed.bozo:
            exc = self.parsed.bozo_exception
            self.error = '%s: %s' % (type(exc), str(exc))
            return

        self.error = None
        if self.xml.getchildren():
            self.xml.remove(self.xml.rss)
        rss = lxml.etree.Element('rss', version='2.0')
        channel = lxml.etree.SubElement(rss, 'channel')

        for src, dest in CHANNEL_MAPPING.items():
            self._append(channel, dest, self.parsed.feed, src)

        if 'image' in self.parsed.feed:
            image = lxml.etree.SubElement(channel, 'image')
            for src, dest in IMAGE_MAPPING.items():
                self._append(image, dest, self.parsed.feed.image, src)

        for entry in self.parsed.entries:
            item = lxml.etree.SubElement(channel, 'item')
            for src, dest in ITEM_MAPPING.items():
                self._append(item, dest, entry, src)

        # append this last, since self.xml is objectified, and
        # objectified doesn't allow manipulating element.text
        self.xml.append(rss)

        self.entry_count = len(self.parsed.entries)

    def _append(self, parent, name, data, key):
        if not key in data:
            return
        elem = lxml.etree.SubElement(parent, name)
        elem.text = unicode(data[key])

    def title(self):
        title = self.xml.xpath('/feed/rss/channel/title')
        if title:
            return str(title[0])
        return ''


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
        if url is None:
            url = ''
        hash_ = md5.new(url).hexdigest()
        try:
            return self.folder[hash_]
        except KeyError:
            feed = Feed()
            feed.url = url
            feed = self.folder[hash_] = feed
            self.refresh_feed(url)
            return self.folder[hash_]

    def refresh_feed(self, url):
        feed = self.get_feed(url)
        with zeit.cms.checkout.helper.checked_out(
                feed, semantic_change=True) as co_feed:
            co_feed.fetch_and_convert()
        #XXX: publish
