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


class TestConflictDetectionBase(object):

    def setUp(self):
        super(TestConflictDetectionBase, self).setUp()
        rid = u'http://xml.zeit.de/testing/conflicting'
        self.connector[rid] = self.get_resource('conflicting', 'Pop.')
        r_a = self.connector[rid]
        self.r_a = self.get_resource(r_a.__name__, r_a.data.read(),
                                     r_a.properties)
        self.connector[rid] = self.get_resource('conflicting', 'Bang.')

    def test_conflict(self):
        self.assertRaises(
            zeit.connector.dav.interfaces.PreconditionFailedError,
            self.connector.add, self.r_a)
        self.assertEquals(
            (None, None, False),
            self.connector.locked(self.r_a.id))

    def test_implicit_override(self):
        del self.r_a.properties[('getetag', 'DAV:')]
        self.connector.add(self.r_a)
        self.assertEquals('Pop.', self.connector[self.r_a.id].data.read())

    def test_explicit_override(self):
        self.connector.add(self.r_a, verify_etag=False)
        self.assertEquals('Pop.', self.connector[self.r_a.id].data.read())

    def test_adding_with_etag_fails(self):
        r = self.get_resource('cannot-be-added', '*Puff*')
        r.properties[('getetag', 'DAV:')] = 'schnutzengrutz'
        self.assertRaises(
            zeit.connector.dav.interfaces.PreconditionFailedError,
            self.connector.add, r)

class TestConflictDetectionReal(
    TestConflictDetectionBase,
    zeit.connector.testing.ConnectorTest):

    pass

class TestConflictDetectionMock(
    TestConflictDetectionBase,
    zeit.connector.testing.MockTest):
    pass

