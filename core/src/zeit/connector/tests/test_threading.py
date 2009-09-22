# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

import StringIO
import random
import thread
import threading
import time
import traceback
import transaction
import zeit.connector.interfaces
import zeit.connector.resource
import zeit.connector.testing
import zope.app.testing.functional
import zope.component
import zope.site.hooks


class ThreadingTest(zope.app.testing.functional.FunctionalTestCase):

    layer = zeit.connector.testing.real_connector_layer
    level = 3

    def setUp(self):
        """Prepares for a functional test case."""
        super(ThreadingTest, self).setUp()
        self.old_site = zope.site.hooks.getSite()
        zope.site.hooks.setSite(self.getRootFolder())
        self.connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        transaction.commit()

    def tearDown(self):
        """Cleans up after a functional test case."""
        transaction.abort()
        super(ThreadingTest, self).tearDown()
        zope.site.hooks.setSite(self.old_site)

    def test_threading(self):
        threads = []
        self.checker = []
        while len(threads) < 10:
            threads.append(threading.Thread(target=self.create_struct))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = [
            '',
            u'/testroot/ folder',
            u'/testroot/a/ folder',
            u'/testroot/a/a/ folder',
            u'/testroot/a/b/ folder',
            u'/testroot/a/b/c/ folder',
            u'/testroot/a/b/c/foo text',
            u'/testroot/a/f text',
            u'/testroot/b/ folder',
            u'/testroot/b/a/ folder',
            u'/testroot/b/b/ folder',
            u'/testroot/b/b/foo text',
            u'/testroot/f text',
            u'/testroot/g text',
            u'/testroot/h text']

        self.assertEquals(10, len(self.checker))
        expected_list = [c for c in self.checker if c != expected]
        self.assertEquals([], expected_list)

    def create_struct(self):
        transaction.abort()
        base = 'http://xml.zeit.de/testing/%s-%s' % (
            str(thread.get_ident()).encode('base64')[:-3], time.time())
        zope.site.hooks.setSite(self.getRootFolder())

        def add_folder(id):
            time.sleep(random.uniform(0, 0.2))
            id = u'%s/%s' % (base, id)
            res = zeit.connector.resource.Resource(
                id, None, 'folder', StringIO.StringIO(''),
                contentType = 'httpd/unix-directory')
            self.connector.add(res)
        def add_file(id):
            time.sleep(random.uniform(0, 0.2))
            id = u'%s/%s' % (base, id)
            res = zeit.connector.resource.Resource(
                id, None, 'text', StringIO.StringIO('Pop.'),
                contentType = 'text/plain')
            self.connector.add(res)

        try:
            add_folder('')
            add_folder('testroot')
            add_folder('testroot/a')
            add_folder('testroot/a/a')
            transaction.commit()
            add_folder('testroot/a/b')
            add_folder('testroot/a/b/c')
            add_folder('testroot/b')
            add_folder('testroot/b/a')
            add_folder('testroot/b/b')
            add_file('testroot/f')
            add_file('testroot/g')
            add_file('testroot/h')
            add_file('testroot/a/f')
            add_file('testroot/a/b/c/foo')
            add_file('testroot/b/b/foo')
            transaction.commit()
        except Exception, e:
            traceback.print_exc()
            transaction.abort()

        result = list_tree(self.connector, base)
        self.checker.append([r.replace(base, '') for r in result])
        try:
            del self.connector[base]
        except Exception, e:
            traceback.print_exc()
        transaction.commit()
