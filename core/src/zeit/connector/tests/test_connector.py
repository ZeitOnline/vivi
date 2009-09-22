# coding: utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

import StringIO
import zeit.connector.resource
import zeit.connector.testing


class TestUnicode(zeit.connector.testing.ConnectorTest):

    def test_access(self):
        r = self.connector[
            u'http://xml.zeit.de/online/2007/09/laktose-milchzucker-gewöhnung']

    def test_create_and_list(self):
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.assertEquals(
            [(u'ünicöde', rid)],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))

    def test_overwrite(self):
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Paff'),
            contentType='text/plain')
        self.assertEquals('Paff', self.connector[rid].data.read())
