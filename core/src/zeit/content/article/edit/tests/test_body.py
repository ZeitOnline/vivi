# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.content.article.testing


class EditableBodyTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(EditableBodyTest, self).setUp()
        import uuid
        self.uuid4 = uuid.uuid4
        uuid.uuid4 = mock.Mock(side_effect=lambda: uuid.uuid4.call_count)

    def tearDown(self):
        import uuid
        uuid.uuid4 = self.uuid4
        super(EditableBodyTest, self).tearDown()

    def get_body(self, body=None):
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        if not body:
            body  = ("<division><p>Para1</p><p/></division>"
                     "<division><p>Para2</p><p/></division>")
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
        self.assertEqual(5, len(body.keys()))
        # Starts at 2 as the first <division> is skipped but still gets a key
        self.assertEqual(['2', '3', '4', '5', '6'], body.keys())

    def test_deleting_division_should_merge_contained_paragraphs(self):
        body = self.get_body()
        # Note: calling for the first time keys() actually makes the keys
        # available.
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

    def test_update_order_should_put_object_into_right_division(self):
        body = self.get_body()
        self.assertEqual(['2', '3', '4', '5', '6'], body.keys())
        body.updateOrder(['2', '3', '5', '4', '6'])
        self.assertEqual(['2', '3', '5', '4', '6'], body.keys())
        body.updateOrder(['2', '4', '5', '3', '6'])
        self.assertEqual(['2', '4', '5', '3', '6'], body.keys())
        del body['2']
        body.updateOrder(['4', '3', '5', '6'])
        self.assertEqual(['4', '3', '5', '6'], body.keys())

    def test_articles_without_division_should_be_migrated(self):
        body = self.get_body(
            '<foo>Honk</foo><p>I have no division</p><p>Only paras</p>')
        self.assertEqual(['2', '3'], body.keys())
        self.assertEqual(
            ['foo', 'division'],
            [child.tag for child in body.xml.iterchildren()])
        self.assertEqual(
            ['p', 'p'],
            [child.tag for child in body.xml.division.iterchildren()])
        self.assertEqual(
            [u'I have no division', u'Only paras'],
            [unicode(child) for child in body.xml.division.iterchildren()])
