from unittest import mock
import unittest

import gocept.testing.assertion
import lxml.etree
import plone.testing.zca
import zope.component
import zope.interface
import zope.schema

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.content.interfaces


class TestDAVConverterWrapper(unittest.TestCase):
    def setUp(self):
        plone.testing.zca.pushGlobalRegistry()

    def tearDown(self):
        plone.testing.zca.popGlobalRegistry()

    def test_get_should_convert_from_property(self):
        from zeit.cms.content.property import DAVConverterWrapper

        prop = mock.Mock()
        prop.__get__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        idpc = mock.Mock()
        zope.component.getSiteManager().registerAdapter(
            idpc,
            required=(zope.interface.Interface, zope.interface.Interface),
            provided=zeit.cms.content.interfaces.IDAVPropertyConverter,
        )
        value = wrap.__get__(mock.sentinel.instance, mock.sentinel.class_)
        # Field is being bound
        field.bind.assert_called_with(mock.sentinel.instance)
        bound_field = field.bind.return_value
        idpc.assert_called_with(bound_field, wrap.DUMMY_PROPERTIES)
        converter = idpc.return_value
        converter.fromProperty.assert_called_with(prop.__get__.return_value)
        self.assertEqual(converter.fromProperty.return_value, value)
        prop.__get__.assert_called_with(mock.sentinel.instance, mock.sentinel.class_)

    def test_set_should_convert_to_property(self):
        from zeit.cms.content.property import DAVConverterWrapper

        prop = mock.Mock()
        prop.__set__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        idpc = mock.Mock()
        zope.component.getSiteManager().registerAdapter(
            idpc,
            required=(zope.interface.Interface, zope.interface.Interface),
            provided=zeit.cms.content.interfaces.IDAVPropertyConverter,
        )
        wrap.__set__(mock.sentinel.instance, mock.sentinel.value)
        # Field is being bound
        field.bind.assert_called_with(mock.sentinel.instance)
        bound_field = field.bind.return_value
        idpc.assert_called_with(bound_field, wrap.DUMMY_PROPERTIES)
        converter = idpc.return_value
        converter.toProperty.assert_called_with(mock.sentinel.value)
        prop.__set__.assert_called_with(mock.sentinel.instance, converter.toProperty.return_value)


class TestStructure(unittest.TestCase, gocept.testing.assertion.Ellipsis):
    def test_setting_missing_value_deletes_xml_content(self):
        from zeit.cms.content.property import Structure

        content = ExampleContentType()
        prop = Structure('.head.foo', zope.schema.Text(missing_value='missing'))
        prop.__set__(content, 'qux')
        self.assertEllipsis('<foo...>qux</foo>', lxml.etree.tostring(content.xml.head.foo))
        prop.__set__(content, 'missing')
        self.assertEllipsis('<foo...xsi:nil="true"/>', lxml.etree.tostring(content.xml.head.foo))


class TestObjectPathProperty(unittest.TestCase, gocept.testing.assertion.Ellipsis):
    def test_setting_none_value_deletes_xml_content(self):
        from zeit.cms.content.property import ObjectPathProperty

        content = ExampleContentType()
        prop = ObjectPathProperty('.raw_query', zope.schema.Text(missing_value='missing'))
        prop.__set__(content, 'solr!')
        self.assertEqual(content.xml.findall('raw_query'), ['solr!'])
        self.assertEllipsis(
            '<raw_query...>solr!</raw_query>', lxml.etree.tostring(content.xml.raw_query)
        )
        prop.__set__(content, None)
        self.assertEqual(content.xml.findall('raw_query'), [])
