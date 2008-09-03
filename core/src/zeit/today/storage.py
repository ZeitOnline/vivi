# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime
import logging
import urllib2
import urlparse
import threading
import time

import lxml.etree
import gocept.lxml.objectify

import zope.interface

import zeit.today.interfaces


logger = logging.getLogger(__name__)


class CountStorage(object):
    """Central access to click counting."""

    zope.interface.implements(zeit.today.interfaces.ICountStorage)

    REFRESH_INTERVAL = 5*60  # 5 minutes

    def __init__(self, url_getter):
        self.url = url_getter
        self.id_to_count = {}
        self.id_to_date = {}
        self.update_lock = threading.Lock()
        self.last_refresh = None

    def get_count(self, unique_id):
        """Return access count for given unique id."""
        self._refresh()
        return self.id_to_count.get(unique_id)

    def get_count_date(self, unique_id):
        """Return access count for given unique id."""
        self._refresh()
        return self.id_to_date.get(unique_id)

    def __iter__(self):
        self._refresh()
        return iter(self.id_to_count)

    def _refresh(self):
        now = time.time()
        if (self.last_refresh
            and self.last_refresh + self.REFRESH_INTERVAL > now):
            return

        locked = self.update_lock.acquire(False)
        if not locked:
            # Some other thread is updating right now, wait until this is
            # finished
            self.update_lock.acquire()
            self.update_lock.release()
            return
        try:
            url = self.url()
            logger.info("Updating click counter from %s" % url)
            request = urllib2.urlopen(url)
            try:
                xml = gocept.lxml.objectify.fromfile(request)
            except lxml.etree.XMLSyntaxError:
                # Hum. Sometimes we cannot parse it because the file is empty.
                # Just ignore this update.
                logger.error("XMLSyntaxError while updating %s" % url,
                             exc_info=True)
            else:
                if xml.find('article') is not None:
                    id_to_count = {}
                    id_to_date = {}
                    for item in xml['article']:
                        url = self._make_unique_id(item.get('url'))
                        count = int(item.get('counter'))
                        date = datetime.date(
                            *(time.strptime(item.get('date'),
                                            '%Y-%m-%d')[0:3]))
                        id_to_count.setdefault(url, 0)
                        id_to_count[url] += count
                        id_to_date[url] = date
                    self.id_to_count = id_to_count
                    self.id_to_date = id_to_date
            self.last_refresh = now
        finally:
            self.update_lock.release()

    @staticmethod
    def _make_unique_id(path):
        while '//' in path:
            path = path.replace('//', '/')
        return urlparse.urljoin('http://xml.zeit.de/', path)


@zope.interface.implementer(zeit.today.interfaces.ICountStorage)
def today_storage_factory():
    def url_getter():
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.today')
        return config['today-xml-url']
    return CountStorage(url_getter)
