# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2
import zeit.content.article.testing
import zope.schema


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
            body = ("<division><p>Para1</p><p/></division>"
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

    def test_adding_to_articles_without_division_should_migrate(self):
        import lxml.objectify
        body = self.get_body(
            '<foo>Honk</foo><p>I have no division</p><p>Only paras</p>')
        ob = mock.Mock()
        ob.__name__ = None
        ob.xml = lxml.objectify.E.ob()
        body.add(ob)
        # XXX assertion?!

    def test_nested_elements_should_be_ignored(self):
        body = self.get_body(
            '<division><p>I have <p>another para</p> in me</p></division>')
        self.assertEqual([u'2'], body.keys())

    def test_adding_division_should_add_on_toplevel(self):
        from zeit.content.article.edit.interfaces import IDivision
        import lxml.objectify
        body = self.get_body('<division/>')
        block = mock.Mock()
        zope.interface.alsoProvides(block, IDivision)
        block.xml = lxml.objectify.E.division()
        block.__name__ = 'myblock'
        block.__parent__ = None
        block.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', 'myblock')
        body.add(block)
        self.assertEqual(2, len(body.xml.getchildren()))


class TestCleaner(unittest2.TestCase):

    def get_article(self):
        from zeit.content.article.article import Article
        return Article()

    def assert_key(self, node, expected):
        have = node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if expected is None:
            self.assertIsNone(have)
        else:
            self.assertEqual(expected, have)

    def set_key(self, node, key):
        node.set('{http://namespaces.zeit.de/CMS/cp}__name__', key)

    def clean(self, obj):
        from zeit.content.article.edit.body import clean_names_on_checkin
        clean_names_on_checkin(obj)

    def test_should_remove_name_attributes(self):
        art = self.get_article()
        art.xml.body.division = ''
        self.set_key(art.xml.body.division, 'divname')
        self.clean(art)
        self.assert_key(art.xml.body.division, None)


class ArticleValidatorTest(zeit.content.article.testing.FunctionalTestCase):

    def test_children_should_return_elements(self):
        import lxml.objectify
        import zeit.content.article.article
        import zeit.content.article.edit.body
        import zeit.edit.interfaces

        body = '<division type="page"><p>Para1</p><p>Para2</p></division>'
        article = zeit.content.article.article.Article()
        article.xml.body = lxml.objectify.XML('<body>%s</body>' % body)
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        validator = zeit.edit.interfaces.IValidator(article)
        self.assertEqual(
            [x.__name__ for x in body.values()],
            [x.__name__ for x in validator.children])


class CheckinTest(zeit.content.article.testing.FunctionalTestCase):

    def test_validation_errors_should_veto_checkin(self):
        from zeit.cms.checkout.interfaces import ICheckinManager
        from zeit.cms.checkout.interfaces import ICheckoutManager
        import zeit.content.article.article

        self.repository['article'] = zeit.content.article.article.Article()

        manager = ICheckoutManager(self.repository['article'])
        co = manager.checkout()
        manager = ICheckinManager(co)
        self.assertFalse(manager.canCheckin)
        errors = dict(manager.last_validation_error)
        self.assertIsInstance(errors['title'], zope.schema.ValidationError)

    def test_security_proxied_fields_should_be_validated_correctly(self):
        from zeit.cms.checkout.interfaces import ICheckinManager
        from zeit.cms.checkout.interfaces import ICheckoutManager
        import zeit.content.article.article

        self.repository['article'] = zeit.content.article.article.Article()

        manager = ICheckoutManager(self.repository['article'])
        co = manager.checkout()
        co = zope.security.proxy.ProxyFactory(co)
        manager = ICheckinManager(co)
        self.assertFalse(manager.canCheckin)
        errors = dict(manager.last_validation_error)
        # the default for keywords is an empty tuple
        self.assertNotIn('keywords', errors)
