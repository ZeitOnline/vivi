import unittest

from zeit.connector.dav.davresource import DAVResource


class TestDAVResource(unittest.TestCase):
    def test_entities_in_url_may_be_part_of_the_path(self):
        res = DAVResource('http://example.com/parks_&amp;_recreation')
        self.assertEqual('/parks_&amp;_recreation', res.path)
