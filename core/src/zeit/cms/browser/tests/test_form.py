# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import absolute_import
import mock
import unittest2 as unittest


class TestApplyDefaultValues(unittest.TestCase):

    def apply(self, interface):
        from ..form import apply_default_values
        context = mock.Mock()
        apply_default_values(context, interface)
        return context

    def test_default_values_should_be_set(self):
        import zope.interface

        class ITest(zope.interface.Interface):
            number = zope.schema.Int(default=26)
        result = self.apply(ITest)
        self.assertEqual(26, result.number)

    def test_false_values_should_be_set(self):
        import zope.interface

        class ITest(zope.interface.Interface):
            yesno = zope.schema.Bool(default=False)
        result = self.apply(ITest)
        self.assertEqual(False, result.yesno)

    def test_none_values_should_not_be_set(self):
        import zope.interface

        class ITest(zope.interface.Interface):
            not_set = zope.schema.Text(default=None)
        result = self.apply(ITest)
        self.assertIsNot(None, result.not_set)
