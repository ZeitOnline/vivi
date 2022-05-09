from unittest.mock import Mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.reference import ReferenceProperty
from zeit.cms.content.reference import SingleReferenceProperty
from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import urllib.error
import urllib.parse
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.cms.testing
import zope.security.management
import zope.security.proxy


class ExampleReference(zeit.cms.content.reference.Reference):

    foo = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'foo')


class ReferenceFixture:

    def setUp(self):
        super().setUp()
        ExampleContentType.references = ReferenceProperty(
            '.body.references.reference', 'test')
        zope.security.protectclass.protectName(
            ExampleContentType, 'references', 'zope.Public')
        zope.security.protectclass.protectSetAttribute(
            ExampleContentType, 'references', 'zope.Public')

        zope.security.protectclass.protectLikeUnto(
            ExampleReference, zeit.cms.content.reference.Reference)
        zope.security.protectclass.protectName(
            ExampleReference, 'foo', 'zope.Public')
        zope.security.protectclass.protectSetAttribute(
            ExampleReference, 'foo', 'zope.Public')

        registry = zope.component.getGlobalSiteManager()
        registry.registerAdapter(
            zeit.cms.related.related.BasicReference, name='test')
        registry.registerAdapter(ExampleReference, name='test')

        self.repository['content'] = ExampleContentType()
        self.repository['target'] = ExampleContentType()

    def tearDown(self):
        del ExampleContentType.references
        super().tearDown()


class ReferencePropertyTest(
        ReferenceFixture, zeit.cms.testing.ZeitCmsTestCase):

    def test_referenced_content_is_accessible_through_reference(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.references = (content.references.create(
            self.repository['target']),)
        self.assertTrue(content._p_changed)
        self.assertEqual(
            'http://xml.zeit.de/target', content.references[0].target.uniqueId)

    def test_setting_to_empty_removes_all_references(self):
        content = self.repository['content']
        content.references = (content.references.create(
            self.repository['target']),)
        content.references = ()
        self.assertEqual((), content.references)

    def test_setting_different_references_is_stored_correctly(self):
        self.repository['other'] = ExampleContentType()
        content = self.repository['content']
        content.references = (
            content.references.create(self.repository['target']),
            content.references.create(self.repository['other']))
        self.assertEqual(
            ['http://xml.zeit.de/target', 'http://xml.zeit.de/other'],
            [x.target.uniqueId for x in content.references])
        content.references = (content.references.create(
            self.repository['target']),)
        self.assertEqual(
            ['http://xml.zeit.de/target'],
            [x.target.uniqueId for x in content.references])

    def test_multiple_references_to_same_object_are_collapsed(self):
        content = self.repository['content']
        content.references = (
            content.references.create(self.repository['target']),
            content.references.create(self.repository['target']))
        self.assertEqual(
            ['http://xml.zeit.de/target'],
            [x.target.uniqueId for x in content.references])

    def test_works_with_security(self):
        content = zope.security.proxy.ProxyFactory(self.repository['content'])
        target = zope.security.proxy.ProxyFactory(self.repository['target'])
        content.references = (content.references.create(target),)
        self.assertEqual(
            'http://xml.zeit.de/target', content.references[0].target.uniqueId)

        ref = content.references[0]
        self.assertEqual(ref, ref)

    def test_reference_to_unknown_content_is_not_returned(self):
        content = self.repository['content']
        content.references = (content.references.create(
            self.repository['target']),)
        del self.repository['target']
        self.assertEqual((), content.references)

    def test_only_creating_a_reference_does_not_set_p_changed_on_source(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.references.create(self.repository['target'])
        self.assertFalse(content._p_changed)

    def test_properties_of_reference_object_are_stored_in_xml(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.references = (content.references.create(
            self.repository['target']),)
        content._p_changed = False

        content.references[0].foo = 'bar'
        self.assertEqual(
            'bar', content.xml.body.references.reference.get('foo'))
        self.assertTrue(content._p_changed)

    def test_metadata_of_reference_is_updated_on_checkin(self):
        self.repository['target'].teaserTitle = 'foo'
        content = self.repository['content']
        with checked_out(content) as co:
            co.references = (co.references.create(
                self.repository['target']),)
        self.assertEqual(
            'foo',
            self.repository['content'].xml.body.references.reference.title)

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = 'bar'
        with checked_out(self.repository['content']):
            pass
        self.assertEqual(
            'bar',
            self.repository['content'].xml.body.references.reference.title)

    def test_set_accepts_references(self):
        content = self.repository['content']
        target = self.repository['target']
        content.references = [content.references.create(target)]
        self.assertEqual([target], [x.target for x in content.references])

    def test_set_raises_given_ICMSContent(self):
        content = self.repository['content']
        target = self.repository['target']
        with self.assertRaises(TypeError) as e:
            content.references = [target]
        self.assertIn('data loss', str(e.exception))

    def test_create_reference_accepts_ICMSContent(self):
        from zeit.cms.content.interfaces import IReference
        content = self.repository['content']
        target = self.repository['target']
        result = ReferenceProperty.create_reference(
            source=content, attribute='references', target=target,
            xml_reference_name='test')
        self.assertTrue(IReference.providedBy(result))
        self.assertEqual(target.uniqueId, result.target.uniqueId)

    def test_create_reference_raises_given_a_reference(self):
        content = self.repository['content']
        with self.assertRaises(TypeError) as e:
            ReferenceProperty.create_reference(
                source=content, attribute='references',
                target=content.references.create(self.repository['target']),
                xml_reference_name='test')
        self.assertIn('data loss', str(e.exception))

    def test_create_reference_raises_given_a_reference_even_if_suppress_error(
            self):
        # Suppressing errors is only forwarded to the XMLReferenceUpdater.
        # It does not mean that the method itself does not raise errors.
        content = self.repository['content']
        with self.assertRaises(TypeError) as e:
            ReferenceProperty.create_reference(
                source=content, attribute='references',
                target=content.references.create(self.repository['target']),
                xml_reference_name='test', suppress_errors=True)
        self.assertIn('data loss', str(e.exception))


class SingleReferenceFixture(ReferenceFixture):

    def setUp(self):
        super().setUp()
        ExampleContentType.references = SingleReferenceProperty(
            '.body.references.reference', 'test')


class SingleReferencePropertyTest(
        SingleReferenceFixture, zeit.cms.testing.ZeitCmsTestCase):

    # XXX This checks basically the same API as the ReferencePropertyTest
    # above, but I'm not sure the benefits of reducing the duplicated test code
    # by extracting the mechanics of setting/getting references outweigh the
    # reduced readiblity.

    def test_referenced_content_is_accessible_through_reference(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        # Check that we can call create() on an empty reference.
        content.references = content.references.create(
            self.repository['target'])
        # Check that we can call create() on a filled reference.
        content.references = content.references.create(
            self.repository['target'])
        self.assertTrue(content._p_changed)
        self.assertEqual(
            'http://xml.zeit.de/target', content.references.target.uniqueId)

    def test_setting_to_empty_removes_reference(self):
        content = self.repository['content']
        content.references = content.references.create(
            self.repository['target'])
        content.references = None
        self.assertFalse(content.references)
        # This is important for formlib
        self.assertEqual(None, content.references)

    def test_works_with_security(self):
        content = zope.security.proxy.ProxyFactory(self.repository['content'])
        target = zope.security.proxy.ProxyFactory(self.repository['target'])
        content.references = content.references.create(target)
        content.references = content.references.create(target)
        self.assertEqual(
            'http://xml.zeit.de/target', content.references.target.uniqueId)


class MultiResourceTest(
        ReferenceFixture, zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        ExampleContentType.related = zeit.cms.content.reference.MultiResource(
            '.body.references.reference', 'test')

    def test_set_and_retrieve_referenced_objects_as_tuple(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.related = (self.repository['target'],)
        self.assertTrue(content._p_changed)
        self.assertIsInstance(content.related, tuple)
        self.assertEqual(
            'http://xml.zeit.de/target', content.related[0].uniqueId)

    def test_should_be_updated_on_checkin(self):
        self.repository['target'].teaserTitle = 'foo'

        content = self.repository['content']
        with checked_out(content) as co:
            co.related = (self.repository['target'],)

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = 'bar'
        with checked_out(self.repository['content']):
            pass

        body = self.repository['content'].xml['body']
        # Since ExampleContentType (our reference target) implements
        # ICommonMetadata, its XMLReferenceUpdater will write 'title' (among
        # others) into the XML.
        self.assertEqual(
            'bar', body['references']['reference']['title'])


class SingleResourceTest(
        ReferenceFixture, zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        ExampleContentType.related = zeit.cms.content.reference.SingleResource(
            '.body.references.reference', 'test')

    def test_set_and_retrieve_referenced_objects_directly(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.related = self.repository['target']
        self.assertTrue(content._p_changed)
        self.assertIsInstance(content.related, ExampleContentType)
        self.assertEqual(
            'http://xml.zeit.de/target', content.related.uniqueId)

    def test_should_be_updated_on_checkin(self):
        self.repository['target'].teaserTitle = 'foo'

        content = self.repository['content']
        with checked_out(content) as co:
            co.related = self.repository['target']

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = 'bar'
        with checked_out(self.repository['content']):
            pass

        body = self.repository['content'].xml['body']
        # Since ExampleContentType (our reference target) implements
        # ICommonMetadata, its XMLReferenceUpdater will write 'title' (among
        # others) into the XML.
        self.assertEqual(
            'bar', body['references']['reference']['title'])


class ReferenceTraversalBase:

    def set_reference(self, obj, value):
        raise NotImplementedError()

    def get_reference(self, obj):
        raise NotImplementedError()

    def test_absolute_url(self):
        with checked_out(self.repository['content']) as co:
            self.set_reference(co, co.references.create(
                self.repository['target']))
        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        b.login('user', 'userpw')
        content = self.repository['content']
        try:
            b.open(
                'http://localhost/++skin++vivi/@@redirect_to?unique_id=%s' % (
                    urllib.parse.quote_plus(
                        self.get_reference(content).uniqueId)))
        except urllib.error.HTTPError as e:
            self.assertEqual(404, e.getcode())
            self.assertIn('/repository/content/++attribute++references', b.url)

    def test_adapting_reference_url_to_cmscontent(self):
        content = self.repository['content']
        self.set_reference(content, content.references.create(
            self.repository['target']))
        reference = self.get_reference(content)
        self.assertEqual(
            reference.target.uniqueId,
            ICMSContent(reference.uniqueId).target.uniqueId)


class ReferenceTraversalTest(
        ReferenceFixture, ReferenceTraversalBase,
        zeit.cms.testing.ZeitCmsBrowserTestCase):

    def set_reference(self, obj, value):
        obj.references = (value,)

    def get_reference(self, obj):
        return obj.references[0]


class SingleReferenceTraversalTest(
        SingleReferenceFixture, ReferenceTraversalBase,
        zeit.cms.testing.ZeitCmsBrowserTestCase):

    def set_reference(self, obj, value):
        obj.references = value

    def get_reference(self, obj):
        return obj.references
