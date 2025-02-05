from unittest import mock
import unittest

import gocept.testing.assertion
import lxml.etree
import plone.testing.zca
import zope.component
import zope.interface
import zope.schema

from zeit.cms.content.property import DAVConverterWrapper, ObjectPathProperty, Structure
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.connector.interfaces import IWebDAVProperties
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.testing


class TestDAVConverterWrapper(unittest.TestCase):
    def setUp(self):
        plone.testing.zca.pushGlobalRegistry()

    def tearDown(self):
        plone.testing.zca.popGlobalRegistry()

    def test_get_should_convert_from_property(self):
        prop = mock.Mock()
        prop.__get__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        idpc = mock.Mock()
        zope.component.getSiteManager().registerAdapter(
            idpc,
            required=(
                zope.interface.Interface,
                zope.interface.Interface,
                zope.interface.Interface,
            ),
            provided=zeit.cms.content.interfaces.IDAVPropertyConverter,
        )
        value = wrap.__get__(mock.sentinel.instance, mock.sentinel.class_)
        # Field is being bound
        field.bind.assert_called_with(mock.sentinel.instance)
        bound_field = field.bind.return_value
        idpc.assert_called_with(bound_field, wrap.DUMMY_PROPERTIES, wrap.DUMMY_PROPERTYKEY)
        converter = idpc.return_value
        converter.fromProperty.assert_called_with(prop.__get__.return_value)
        self.assertEqual(converter.fromProperty.return_value, value)
        prop.__get__.assert_called_with(mock.sentinel.instance, mock.sentinel.class_)

    def test_set_should_convert_to_property(self):
        prop = mock.Mock()
        prop.__set__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        idpc = mock.Mock()
        zope.component.getSiteManager().registerAdapter(
            idpc,
            required=(
                zope.interface.Interface,
                zope.interface.Interface,
                zope.interface.Interface,
            ),
            provided=zeit.cms.content.interfaces.IDAVPropertyConverter,
        )
        wrap.__set__(mock.sentinel.instance, mock.sentinel.value)
        # Field is being bound
        field.bind.assert_called_with(mock.sentinel.instance)
        bound_field = field.bind.return_value
        idpc.assert_called_with(bound_field, wrap.DUMMY_PROPERTIES, wrap.DUMMY_PROPERTYKEY)
        converter = idpc.return_value
        converter.toProperty.assert_called_with(mock.sentinel.value)
        prop.__set__.assert_called_with(mock.sentinel.instance, converter.toProperty.return_value)


class TestStructure(unittest.TestCase, gocept.testing.assertion.Ellipsis):
    def test_setting_missing_value_deletes_xml_content(self):
        content = ExampleContentType()
        prop = Structure('.head.foo', zope.schema.Text(missing_value='missing'))
        prop.__set__(content, 'qux')
        self.assertEllipsis('<foo...>qux</foo>', lxml.etree.tostring(content.xml.find('head/foo')))
        prop.__set__(content, 'missing')
        self.assertEllipsis(
            '<foo...xsi:nil="true"/>', lxml.etree.tostring(content.xml.find('head/foo'))
        )


class TestObjectPathProperty(unittest.TestCase, gocept.testing.assertion.Ellipsis):
    def test_setting_none_value_deletes_xml_content(self):
        content = ExampleContentType()
        prop = ObjectPathProperty('.example', zope.schema.Text(missing_value='missing'))
        prop.__set__(content, 'foo')
        self.assertEllipsis(
            '<example...>foo</example>', lxml.etree.tostring(content.xml.find('example'))
        )
        prop.__set__(content, None)
        self.assertEqual(content.xml.findall('example'), [])


class TestXMLOrDAVProperty(zeit.cms.testing.ZeitCmsTestCase):
    DOCUMENT = 'http://namespaces.zeit.de/CMS/document'

    def setUp(self):
        super().setUp()
        self.content = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['testcontent']
        ).checkout()
        # Storing the descriptor on an instance allows us to use it "standalone".
        self.prop = ObjectPathProperty(
            '.example',
            zope.schema.Text(),
            dav_ns=self.DOCUMENT,
            dav_name='foo',
            dav_toggle='always',
        )

    def test_reads_from_dav_property(self):
        IWebDAVProperties(self.content)[('foo', self.DOCUMENT)] = 'foo'
        self.assertEqual('foo', self.prop.__get__(self.content, type(self.content)))

    def test_writes_to_dav_property(self):
        self.prop.__set__(self.content, 'foo')
        self.assertEllipsis(
            '<example...>foo</example>', lxml.etree.tostring(self.content.xml.find('example'))
        )
        self.assertEqual('foo', IWebDAVProperties(self.content)[('foo', self.DOCUMENT)])

    def test_toggle_strict_does_not_write_to_xml(self):
        FEATURE_TOGGLES.set('xmlproperty_strict_always')
        self.prop.__set__(self.content, 'foo')
        self.assertEqual(None, self.content.xml.find('example'))
        self.assertEqual('foo', IWebDAVProperties(self.content)[('foo', self.DOCUMENT)])
