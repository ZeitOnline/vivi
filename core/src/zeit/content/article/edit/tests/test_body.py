from unittest import mock
from zeit.cms.checkout.interfaces import ICheckinManager
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.content.article.edit.interfaces import IDivision
import gocept.testing.mock
import lxml.objectify
import six
import unittest
import zeit.cms.testing
import zeit.content.article.article
import zeit.content.article.edit.body
import zeit.content.article.testing
import zeit.edit.interfaces
import zope.schema


class EditableBodyTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        self.patches = gocept.testing.mock.Patches()
        fake_uuid = mock.Mock()
        fake_uuid.side_effect = lambda: 'id-%s' % fake_uuid.call_count
        self.patches.add(
            'zeit.edit.container.Base._generate_block_id', fake_uuid)

    def tearDown(self):
        self.patches.reset()
        super().tearDown()

    def get_body(self, body=None):
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
        self.assertEqual(['id-2', 'id-3', 'id-4', 'id-5', 'id-6'], body.keys())

    def test_deleting_division_should_merge_contained_paragraphs(self):
        body = self.get_body()
        # Note: calling for the first time keys() actually makes the keys
        # available.
        self.assertEqual(['id-2', 'id-3', 'id-4', 'id-5', 'id-6'], body.keys())
        del body['id-4']
        self.assertEqual(['id-2', 'id-3', 'id-5', 'id-6'], body.keys())

    def test_add_should_add_to_last_division(self):
        body = self.get_body('<division/>')
        block = mock.Mock()
        block.xml = lxml.objectify.E.mockblock()
        block.__name__ = 'myblock'
        block.__parent__ = None
        block.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', 'myblock')
        body.add(block)
        self.assertEqual(['myblock'], body.keys())

    def test_update_order_should_put_object_into_right_division(self):
        body = self.get_body()
        self.assertEqual(['id-2', 'id-3', 'id-4', 'id-5', 'id-6'], body.keys())
        body.updateOrder(['id-2', 'id-3', 'id-5', 'id-4', 'id-6'])
        self.assertEqual(['id-2', 'id-3', 'id-5', 'id-4', 'id-6'], body.keys())
        body.updateOrder(['id-2', 'id-4', 'id-5', 'id-3', 'id-6'])
        self.assertEqual(['id-2', 'id-4', 'id-5', 'id-3', 'id-6'], body.keys())
        del body['id-2']
        body.updateOrder(['id-4', 'id-3', 'id-5', 'id-6'])
        self.assertEqual(['id-4', 'id-3', 'id-5', 'id-6'], body.keys())

    def test_articles_without_division_should_be_migrated(self):
        body = self.get_body(
            '<foo>Honk</foo><p>I have no division</p><p>Only paras</p>')
        self.assertEqual(['id-2', 'id-3'], body.keys())
        self.assertEqual(
            ['foo', 'division'],
            [child.tag for child in body.xml.iterchildren()])
        self.assertEqual(
            ['p', 'p'],
            [child.tag for child in body.xml.division.iterchildren()])
        self.assertEqual(
            ['I have no division', 'Only paras'],
            [six.text_type(child) for child
             in body.xml.division.iterchildren()])

    def test_adding_to_articles_without_division_should_migrate(self):
        body = self.get_body(
            '<foo>Honk</foo><p>I have no division</p><p>Only paras</p>')
        ob = mock.Mock()
        ob.__name__ = None
        ob.__parent__ = None
        ob.xml = lxml.objectify.E.ob()
        body.add(ob)
        # XXX assertion?!

    def test_nested_elements_should_be_ignored(self):
        body = self.get_body(
            '<division><p>I have <p>another para</p> in me</p></division>')
        self.assertEqual(['id-2'], body.keys())

    def test_adding_division_should_add_on_toplevel(self):
        body = self.get_body('<division/>')
        block = mock.Mock()
        zope.interface.alsoProvides(block, IDivision)
        block.xml = lxml.objectify.E.division()
        block.__name__ = 'myblock'
        block.__parent__ = None
        block.xml.set('{http://namespaces.zeit.de/CMS/cp}__name__', 'myblock')
        body.add(block)
        self.assertEqual(2, len(body.xml.getchildren()))

    def test_values_does_not_set_block_ids(self):
        body = self.get_body()

        def find_id_attributes():
            return body.xml.xpath(
                '//*[@ns:__name__]',
                namespaces={'ns': 'http://namespaces.zeit.de/CMS/cp'})

        self.assertFalse(find_id_attributes())
        body.values()
        self.assertFalse(find_id_attributes())
        body.keys()
        self.assertTrue(find_id_attributes())

    def test_values_returns_same_blocks_as_keys(self):
        body = self.get_body()
        self.assertEqual(
            [x.xml for x in body.values()],
            [body[x].xml for x in body.keys()])

    def test_ignores_xml_comments(self):
        body = self.get_body('<division><p>foo</p><!-- comment --></division>')
        self.assertEqual(1, len(body.keys()))


class TestCleaner(unittest.TestCase):

    def get_article(self):
        return zeit.content.article.article.Article()

    def assert_key(self, node, expected):
        have = node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if expected is None:
            self.assertIsNone(have)
        else:
            self.assertEqual(expected, have)

    def set_key(self, node, key):
        node.set('{http://namespaces.zeit.de/CMS/cp}__name__', key)

    def clean(self, obj):
        from zeit.content.article.edit.body import remove_name_attributes
        remove_name_attributes(obj, mock.sentinel.event)

    def test_should_remove_name_attributes(self):
        art = self.get_article()
        art.xml.body.division = ''
        self.set_key(art.xml.body.division, 'divname')
        self.clean(art)
        self.assert_key(art.xml.body.division, None)

    def test_should_remove_namespace(self):
        art = self.get_article()
        art.xml.body.division = ''
        self.set_key(art.xml.body.division, 'divname')
        self.clean(art)
        self.assertNotIn(
            'namespaces.zeit.de/CMS/cp', zeit.cms.testing.xmltotext(art.xml))


class ArticleValidatorTest(zeit.content.article.testing.FunctionalTestCase):

    def test_children_should_return_elements(self):
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
        self.repository['article'] = zeit.content.article.article.Article()
        manager = ICheckoutManager(self.repository['article'])
        co = manager.checkout()
        manager = ICheckinManager(co)
        self.assertFalse(manager.canCheckin)
        errors = dict(manager.last_validation_error)
        self.assertIsInstance(
            errors['title'], zope.schema.ValidationError)

    def test_security_proxied_fields_should_be_validated_correctly(self):
        self.repository['article'] = zeit.content.article.article.Article()
        manager = ICheckoutManager(self.repository['article'])
        co = manager.checkout()
        co = zope.security.proxy.ProxyFactory(co)
        manager = ICheckinManager(co)
        self.assertFalse(manager.canCheckin)
        errors = dict(manager.last_validation_error)
        # the default for keywords is an empty tuple
        self.assertNotIn('keywords', errors)

    def test_validation_errors_should_consider_teaser_image(self):
        self.repository['article'] = zeit.content.article.article.Article()
        manager = ICheckoutManager(self.repository['article'])
        co = manager.checkout()
        zeit.cms.content.field.apply_default_values(
            co, zeit.content.article.interfaces.IArticle)
        img = zeit.content.image.interfaces.IImages(co)
        img.fill_color = '#xxxxxx'
        manager = ICheckinManager(co)
        self.assertFalse(manager.canCheckin)
        errors = dict(manager.last_validation_error)
        self.assertIsInstance(
            errors['fill_color'], zope.schema.ValidationError)
