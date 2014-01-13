# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from mock import Mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.reference import ReferenceProperty
from zeit.cms.interfaces import ICMSContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import urllib
import urllib2
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.cms.testing
import zope.security.management
import zope.security.proxy
import zope.testbrowser.testing


class ExampleReference(zeit.cms.content.reference.Reference):

    foo = zeit.cms.content.property.ObjectPathAttributeProperty('.', 'foo')


class ReferenceFixture(object):

    def setUp(self):
        super(ReferenceFixture, self).setUp()
        TestContentType.references = ReferenceProperty(
            '.body.references.reference', 'test')
        zope.security.protectclass.protectName(
            TestContentType, 'references', 'zope.Public')
        zope.security.protectclass.protectSetAttribute(
            TestContentType, 'references', 'zope.Public')

        zope.security.protectclass.protectLikeUnto(
            ExampleReference, zeit.cms.content.reference.Reference)
        zope.security.protectclass.protectName(
            ExampleReference, 'foo', 'zope.Public')
        zope.security.protectclass.protectSetAttribute(
            ExampleReference, 'foo', 'zope.Public')

        self.zca.patch_adapter(
            zeit.cms.related.related.BasicReference, name='test')
        self.zca.patch_adapter(ExampleReference, name='test')

        self.repository['content'] = TestContentType()
        self.repository['target'] = TestContentType()

    def tearDown(self):
        del TestContentType.references
        super(ReferenceFixture, self).tearDown()


class ReferencePropertyTest(
        ReferenceFixture, zeit.cms.testing.FunctionalTestCase):

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
        self.repository['other'] = TestContentType()
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

    def test_works_with_security(self):
        content = zope.security.proxy.ProxyFactory(self.repository['content'])
        target = zope.security.proxy.ProxyFactory(self.repository['target'])
        content.references = (content.references.create(target),)
        self.assertEqual(
            'http://xml.zeit.de/target', content.references[0].target.uniqueId)

    def test_reference_to_unknown_content_is_not_returned(self):
        content = self.repository['content']
        content.references = (content.references.create(
            self.repository['target']),)
        del self.repository['target']
        self.assertEqual((), content.references)

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
        self.repository['target'].teaserTitle = u'foo'
        content = self.repository['content']
        with checked_out(content) as co:
            co.references = (co.references.create(
                self.repository['target']),)
        self.assertEqual(
            u'foo',
            self.repository['content'].xml.body.references.reference.title)

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = u'bar'
        with checked_out(self.repository['content']):
            pass
        self.assertEqual(
            u'bar',
            self.repository['content'].xml.body.references.reference.title)


class MultiResourceTest(
        ReferenceFixture, zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(MultiResourceTest, self).setUp()
        TestContentType.related = zeit.cms.content.reference.MultiResource(
            '.body.references.reference', 'test')

    def test_set_and_retrieve_referenced_objects_as_tuple(self):
        content = self.repository['content']
        content._p_jar = Mock()  # make _p_changed work
        content.related = (self.repository['target'],)
        self.assertTrue(content._p_changed)
        self.assertIsInstance(content.related, tuple)
        self.assertEqual(
            'http://xml.zeit.de/target', content.related[0].uniqueId)

    def test_setting_existing_references_leaves_xml_node_alone(self):
        self.repository['other'] = TestContentType()
        content = self.repository['content']
        content.related = (self.repository['target'],)
        # both .references and .related use the same xpath
        content.references[0].foo = 'bar'
        content.related = (
            self.repository['target'], self.repository['other'])
        self.assertEqual(
            'bar', content.xml.body.references.reference.get('foo'))

    def test_should_be_updated_on_checkin(self):
        self.repository['target'].teaserTitle = u'foo'

        content = self.repository['content']
        with checked_out(content) as co:
            co.related = (self.repository['target'],)

        with checked_out(self.repository['target']) as co:
            co.teaserTitle = u'bar'
        with checked_out(self.repository['content']):
            pass

        body = self.repository['content'].xml['body']
        # Since TestContentType (our reference target) implements
        # ICommonMetadata, its XMLReferenceUpdater will write 'title' (among
        # others) into the XML.
        self.assertEqual(
            u'bar', body['references']['reference']['title'])


class ReferenceTraversalTest(
        ReferenceFixture, zeit.cms.testing.FunctionalTestCase):

    def test_absolute_url(self):
        with checked_out(self.repository['content']) as co:
            co.references = (co.references.create(
                self.repository['target']),)
        b = zope.testbrowser.testing.Browser()
        zope.security.management.endInteraction()
        b.addHeader('Authorization', 'Basic user:userpw')
        content = self.repository['content']
        try:
            b.open(
                'http://localhost/++skin++vivi/@@redirect_to?unique_id=%s' % (
                    urllib.quote_plus(content.references[0].uniqueId)))
        except urllib2.HTTPError, e:
            self.assertEqual(404, e.getcode())
            self.assertIn('/repository/content/++attribute++references', b.url)

    def test_adapting_reference_url_to_cmscontent(self):
        content = self.repository['content']
        content.references = (content.references.create(
            self.repository['target']),)
        self.assertEqual(
            content.references[0].target.uniqueId,
            ICMSContent(content.references[0].uniqueId).target.uniqueId)
