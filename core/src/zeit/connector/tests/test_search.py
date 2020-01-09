# coding: utf8
import unittest


class TestSearchVar(unittest.TestCase):

    def test_unicode_value_should_be_encoded_utf8(self):
        from zeit.connector.search import SearchVar
        author = SearchVar('author', 'namespace')
        self.assertEqual(
            '(:eq "namespace" "author" "Fröbel")',
            (author == u'Fröbel')._render())
