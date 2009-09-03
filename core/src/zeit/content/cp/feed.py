# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import datetime
import feedparser
import gocept.runner
import logging
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
import zeit.cms.workflow.interfaces
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

        self.error = None
        self.last_update = datetime.datetime.now(pytz.UTC)
        if not self.url:
            self.error = "No or invaid URL."
            return
        url = self.url
        if url.startswith('file://'):
            url = url.replace('file://', '', 1)
        parsed = feedparser.parse(url)
        if parsed.bozo:
            exc = parsed.bozo_exception
            self.error = '%s: %s' % (type(exc).__name__, str(exc))
            return

        if self.xml.getchildren():
            self.xml.remove(self.xml.rss)
        rss = lxml.etree.Element('rss', version='2.0')
        channel = lxml.etree.SubElement(rss, 'channel')
        for src, dest in CHANNEL_MAPPING.items():
            self._append(channel, dest, parsed.feed, src)

        if 'image' in parsed.feed:
            image = lxml.etree.SubElement(channel, 'image')
            for src, dest in IMAGE_MAPPING.items():
                self._append(image, dest, parsed.feed.image, src)

        # XXX thank you feedparser for the non-uniform API :-(
        if hasattr(parsed.feed, 'categories'):
            for domain, value in parsed.feed.categories:
                self._append_category(channel, domain, value)

        for entry in parsed.entries:
            item = lxml.etree.SubElement(channel, 'item')
            for src, dest in ITEM_MAPPING.items():
                self._append(item, dest, entry, src)

            if hasattr(entry, 'categories'):
                for domain, value in entry.categories:
                    self._append_category(item, domain, value)

        # append this last, since self.xml is objectified, and
        # objectified doesn't allow manipulating element.text
        self.xml.append(rss)

        self.entry_count = len(parsed.entries)

    def _append(self, parent, name, data, key):
        if not key in data:
            return
        elem = lxml.etree.SubElement(parent, name)
        elem.text = unicode(data[key])

    def _append_category(self, parent, domain, value):
        category = lxml.etree.SubElement(parent, 'category')
        if domain:
            category.set('domain', domain)
        category.text = value

    @property
    def title(self):
        title = self.xml.xpath('/feed/rss/channel/title')
        return unicode(title[0]) if title else ''

    @property
    def entries(self):
        return [unicode(x.text) for x in self.xml.xpath(
            '/feed/rss/channel/item/title')]


class FeedType(zeit.cms.type.XMLContentTypeDeclaration):

    interface = zeit.content.cp.interfaces.IFeed
    type = 'feed'
    register_as_type = False
    factory = Feed


class FeedValidator(object):

    zope.interface.implements(zeit.content.cp.interfaces.IValidator)

    status = None

    def __init__(self, context):
        self.messages = []
        self.context = context
        if self.context.error:
            self.status = zeit.content.cp.rule.ERROR
            self.messages.append(self.context.error)


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
        if not url:
            return
        hash_ = md5.new(url).hexdigest()
        if hash_ in self.folder:
            return self.folder[hash_]
        else:
            feed = Feed()
            feed.url = url
            self.folder[hash_] = feed
            self.refresh_feed(url)
            return self.folder[hash_]

    def refresh_feed(self, url):
        feed = self.get_feed(url)
        with zeit.cms.checkout.helper.checked_out(
                feed, semantic_change=True, events=False) as co_feed:
            # We don't need to send events here as a full checkout/checkin
            # cycle is done duing publication anyway. Also when sending events
            # async tasks are done in parallel to publishing which isn't nice
            # either (conflicts).
            co_feed.fetch_and_convert()
        try:
            zeit.cms.workflow.interfaces.IPublish(feed).publish()
        except zeit.cms.workflow.interfaces.PublishingError:
            # This is raised when there are errors in the feed. It will not
            # be published then.
            pass


def _refresh_all():
    logger = logging.getLogger('zeit.content.cp.feed')
    logger.info('refresh_all() started')
    fm = zope.component.getUtility(zeit.content.cp.interfaces.IFeedManager)
    now = datetime.datetime.now(pytz.UTC)
    interval = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')['feed-update-minimum-age']
    for feed in fm.folder.values():
        if now > feed.last_update + datetime.timedelta(minutes=int(interval)):
            logger.info('Refreshing feed for <%s>' % feed.url)
            fm.refresh_feed(feed.url)
        else:
            logger.info('Not refreshing feed for <%s>, last_update=%s'
                        % (feed.url, feed.last_update))

    logger.info('refresh_all() done')


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.content.cp', 'feed-invalidation-principal'))
def refresh_all():
    _refresh_all()
