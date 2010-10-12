# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.content.article.testing


class EditableBodyTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.article.testing.ArticleLayer

    def get_body(self, body=None):
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body  = ("<division><p>Para1</p><img/></division>"
                     "<division><p>Para2</p><foo/></division>")
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML(
            '<body>%s</body>' % body)
        for division in article.xml.body.findall('division'):
            division.set('type', 'page')
        return zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)

    def test_keys_contain_division_contents(self):
        body = self.get_body()
        # The first division is omitted, thus only 5 keys
        with mock.patch('uuid.uuid4') as uuid:
            uuid.side_effect = lambda: uuid.call_count
            self.assertEqual(5, len(body.keys()))
        # Starts at 2 as the first <division> is skipped but still gets a key
        self.assertEqual(['2', '3', '4', '5', '6'], body.keys())

    def test_deleting_division_should_merge_contained_paragraphs(self):
        body = self.get_body()
        # Note: calling for the first time keys() actually makes the keys
        # available.
        with mock.patch('uuid.uuid4') as uuid:
            uuid.side_effect = lambda: uuid.call_count
            self.assertEqual(['2', '3', '4', '5', '6'], body.keys())
        del body['4']
        self.assertEqual(['2', '3', '5', '6'], body.keys())

    def test_add_should_add_to_last_division(self):
        import lxml.objectify
        body = self.get_body('<division/>')
        block = mock.Mock()
        block.xml = lxml.objectify.E.mockblock()
        block.__name__ = 'myblock'
        block.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', 'myblock')
        body.add(block)
        self.assertEqual(['myblock'], body.keys())


