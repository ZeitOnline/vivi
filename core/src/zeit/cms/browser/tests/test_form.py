# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import absolute_import
import unittest2 as unittest
import zeit.cms.browser.form
import zeit.cms.testing
import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema


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


class ITestSchema(zope.interface.Interface):

    line = zope.schema.TextLine(title=u'text line')

    text = zope.schema.Text(title=u'text')

    check = zope.schema.Bool(title=u'check')


class TestAddForm(zeit.cms.browser.form.AddForm):

    form_fields = zope.formlib.form.Fields(ITestSchema)


class Placeholder(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(Placeholder, self).setUp()
        self.form = TestAddForm(
            object(), zope.publisher.browser.TestRequest())

    def test_text_input_widgets_get_placeholder(self):
        self.form.setUpWidgets()
        self.assertEqual(
            'placeholder="text line"', self.form.widgets['line'].extra)

    def test_textarea_widgets_get_placeholder(self):
        self.form.setUpWidgets()
        self.assertEqual(
            'placeholder="text"', self.form.widgets['text'].extra)

    def test_non_text_widget_is_not_affected(self):
        self.form.setUpWidgets()
        self.assertEqual('', self.form.widgets['check'].extra)
