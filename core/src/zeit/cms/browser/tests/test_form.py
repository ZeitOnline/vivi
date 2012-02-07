# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import absolute_import
import unittest2 as unittest
import zope.interface


class Test(object):
    """Don't use a mock for this because getting a non-existing attribute from
    a mock yields a non-None value.
    """


class TestApplyDefaultValues(unittest.TestCase):

    def apply(self, interface, context=None):
        from ..form import apply_default_values
        if context is None:
            context = Test()
        apply_default_values(context, interface)
        return context

    def test_default_values_should_be_set(self):
        class ITest(zope.interface.Interface):
            number = zope.schema.Int(default=26)
        result = self.apply(ITest)
        self.assertEqual(26, result.number)

    def test_false_values_should_be_set(self):
        class ITest(zope.interface.Interface):
            yesno = zope.schema.Bool(default=False)
        result = self.apply(ITest)
        self.assertEqual(False, result.yesno)

    def test_none_values_should_not_be_set(self):
        class ITest(zope.interface.Interface):
            not_set = zope.schema.Text(default=None)
        result = self.apply(ITest)
        self.assertFalse(hasattr(result, 'not_set'))

    def test_existing_values_should_not_be_overwritten(self):
        class ITest(zope.interface.Interface):
            number = zope.schema.Int(default=42)
        context = Test()
        context.number = 24
        context = self.apply(ITest, context)
        self.assertEqual(24, context.number)

    def test_none_should_not_be_overwritten_if_valid(self):
        class ITest(zope.interface.Interface):
            number = zope.schema.Int(default=42, required=False)
        context = Test()
        context.number = None
        context = self.apply(ITest, context)
        self.assertIsNone(context.number)
