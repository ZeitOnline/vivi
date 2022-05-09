import unittest
import zeit.cms.browser.form
import zeit.cms.testing
import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema


class DummyContext:
    """Don't use a mock for this because getting a non-existing attribute from
    a mock yields a non-None value.
    """


class ApplyDefaultValuesTests(unittest.TestCase):

    def apply(self, interface, context=None):
        from zeit.cms.content.field import apply_default_values
        if context is None:
            context = DummyContext()
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
        context = DummyContext()
        context.number = 24
        context = self.apply(ITest, context)
        self.assertEqual(24, context.number)


class ITestSchema(zope.interface.Interface):

    line = zope.schema.TextLine(title='text line')

    text = zope.schema.Text(title='text')

    check = zope.schema.Bool(title='check')

    special = zope.schema.Text(title='special')
    special.setTaggedValue('placeholder', 'customised')


class ExampleAddForm(zeit.cms.browser.form.AddForm):

    form_fields = zope.formlib.form.Fields(ITestSchema)


class Placeholder(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        self.form = ExampleAddForm(
            object(), zope.publisher.browser.TestRequest())
        self.form.factory = object

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

    def test_placeholder_is_looked_up_in_fields_tagged_values(self):
        self.form.setUpWidgets()
        self.assertEqual(
            'placeholder="customised"', self.form.widgets['special'].extra)


class CharlimitForm(zeit.cms.browser.form.EditForm,
                    zeit.cms.browser.form.CharlimitMixin):

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.set_charlimit('foo')


class CharlimitTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_tagged_value_for_charlimit_is_used(self):

        class Schema(zope.interface.Interface):
            foo = zope.schema.TextLine()
            foo.setTaggedValue('zeit.cms.charlimit', 70)

        @zope.interface.implementer(Schema)
        class Context:
            foo = "bar"

        form = CharlimitForm(Context(), zope.publisher.browser.TestRequest())
        form.form_fields = zope.formlib.form.FormFields(Schema)
        form.setUpWidgets()
        widget = form.widgets['foo']
        self.assertEllipsis('...cms:charlimit="70"...', widget())

    def test_charlimit_falls_back_to_max_length(self):

        class Schema(zope.interface.Interface):
            foo = zope.schema.TextLine(max_length=70)

        @zope.interface.implementer(Schema)
        class Context:
            foo = "bar"

        form = CharlimitForm(Context(), zope.publisher.browser.TestRequest())
        form.form_fields = zope.formlib.form.FormFields(Schema)
        form.setUpWidgets()
        widget = form.widgets['foo']
        self.assertEllipsis('...cms:charlimit="70"...', widget())
