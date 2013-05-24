# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest


class TestHTMLContent(unittest.TestCase):

    def test_get_tree_should_append_text(self):
        from zeit.content.gallery.gallery import Gallery, HTMLContent
        gallery = Gallery()
        html = HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))

    def test_get_tree_should_return_existing_text(self):
        from zeit.content.gallery.gallery import Gallery, HTMLContent
        gallery = Gallery()
        gallery.xml.body['text'] = 'honk'
        html = HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual('honk', tree.text)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))
