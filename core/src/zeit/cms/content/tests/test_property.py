# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest


class TestDAVConverterWrapper(unittest.TestCase):

    def test_get_should_convert_from_property(self):
        from zeit.cms.content.property import DAVConverterWrapper
        prop = mock.Mock()
        prop.__get__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        with mock.patch('zeit.cms.content.interfaces.IDAVPropertyConverter') \
                as idpc:
            value = wrap.__get__(mock.sentinel.instance, mock.sentinel.class_)
            # Field is being bound
            field.bind.assert_called_with(mock.sentinel.instance)
            bound_field = field.bind.return_value
            idpc.assert_called_with(bound_field)
            converter = idpc.return_value
            converter.fromProperty.assert_called_with(
                prop.__get__.return_value)
            self.assertEqual(converter.fromProperty.return_value, value)
            prop.__get__.assert_called_with(mock.sentinel.instance,
                                            mock.sentinel.class_)

    def test_set_should_convert_to_property(self):
        from zeit.cms.content.property import DAVConverterWrapper
        prop = mock.Mock()
        prop.__set__ = mock.Mock()
        field = mock.Mock()
        wrap = DAVConverterWrapper(prop, field)
        with mock.patch('zeit.cms.content.interfaces.IDAVPropertyConverter') \
                as idpc:
            wrap.__set__(mock.sentinel.instance, mock.sentinel.value)
            # Field is being bound
            field.bind.assert_called_with(mock.sentinel.instance)
            bound_field = field.bind.return_value
            idpc.assert_called_with(bound_field)
            converter = idpc.return_value
            converter.toProperty.assert_called_with(mock.sentinel.value)
            prop.__set__.assert_called_with(
                mock.sentinel.instance, converter.toProperty.return_value)
