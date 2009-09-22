# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import ZODB.blob
import os
import pkg_resources
import unittest
import zc.queue.tests
import zeit.connector.connector
import zope.app.testing.functional


real_connector_layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, 'ConnectorLayer', allow_teardown=True)


optionflags=(doctest.REPORT_NDIFF + doctest.NORMALIZE_WHITESPACE +
             doctest.ELLIPSIS + doctest.INTERPRET_FOOTNOTES)


class ConnectorTest(unittest.TestCase):

    def setUp(self):
        super(ConnectorTest, self).setUp()
        self.connector = zeit.connector.connector.Connector(
            roots={"default": os.environ['connector-url']})

    def tearDown(self):
        for name, uid in self.connector.listCollection(
            'http://xml.zeit.de/testing/'):
            del self.connector[uid]


def get_storage(blob_dir):
    storage = zc.queue.tests.ConflictResolvingMappingStorage('test')
    blob_storage = ZODB.blob.BlobStorage(blob_dir, storage)
    return blob_storage


def print_tree(connector, base):
    """Helper to print a tree."""
    print '\n'.join(list_tree(connector, base))


def list_tree(connector, base, level=0):
    """Helper to print a tree."""
    result = []
    if level == 0:
        result.append(base)
    for name, uid in sorted(connector.listCollection(base)):
        result.append('%s %s' % (uid, connector[uid].type))
        if uid.endswith('/'):
            result.extend(list_tree(connector, uid, level+1))

    return result
