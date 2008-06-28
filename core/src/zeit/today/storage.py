# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

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

    def __init__(self):
        self.id_to_count = {}
        self.update_lock = threading.Lock()
        self.last_refresh = None

    def get_count(self, unique_id):
        """Return access count for given unique id."""
        self._refresh()
        return self.id_to_count.get(unique_id)

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
            config = zope.app.appsetup.product.getProductConfiguration(
                'zeit.today')
            url = config['today-xml-url']
            logger.info("Updating click counter from %s" % url)
            request = urllib2.urlopen(url)
            try:
                xml = gocept.lxml.objectify.fromfile(request)
            except lxml.etree.XMLSyntaxError:
                # Hum. Sometimes we cannot parse it because the file is empty.
                # Just ignore this update.
                logger.error("XMLSyntaxError while updating today.xml")
            else:
                self.id_to_count = dict(
                    (self._make_unique_id(item.get('url')),
                     int(item.get('counter'))) for item in xml.article)
            self.last_refresh = now
        finally:
            self.update_lock.release()

    @staticmethod
    def _make_unique_id(path):
        return urlparse.urljoin('http://xml.zeit.de', path)
