import unittest
import zeit.content.gallery.gallery


class TestHTMLContent(unittest.TestCase):

    def test_get_tree_should_append_text(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        html = zeit.content.gallery.gallery.HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))

    def test_get_tree_should_return_existing_text(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.xml.body['text'] = 'honk'
        html = zeit.content.gallery.gallery.HTMLContent(gallery)
        tree = html.get_tree()
        self.assertEqual('text', tree.tag)
        self.assertEqual('honk', tree.text)
        self.assertEqual(1, len(gallery.xml.body.findall('text')))
