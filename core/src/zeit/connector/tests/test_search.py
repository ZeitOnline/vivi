# coding: utf8
# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest


class TestSearchVar(unittest.TestCase):

    def test_unicode_value_should_be_encoded_utf8(self):
        from zeit.connector.search import SearchVar
        author = SearchVar('author', 'namespace')
        self.assertEqual(
            '(:eq "namespace" "author" "Fr\xc3\xb6bel")',
            (author == u'Fröbel')._render())
