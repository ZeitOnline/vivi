import zeit.cms.browser.form
import zeit.cms.testing
import zeit.content.article.edit.browser.form
import zope.formlib.form
import zope.interface
import zope.publisher.browser
import zope.schema
# XXX This should really be extracted from the article editor.


class Form(zeit.cms.browser.form.EditForm,
           zeit.content.article.edit.browser.form.CharlimitMixin):

    def setUpWidgets(self, *args, **kw):
        super(Form, self).setUpWidgets(*args, **kw)
        self.set_charlimit('foo')


class CharlimitTest(zeit.cms.testing.FunctionalTestCase):

    def test_tagged_value_for_charlimit_is_used(self):

        class Schema(zope.interface.Interface):
            foo = zope.schema.TextLine()
            foo.setTaggedValue('zeit.cms.charlimit', 70)

        class Context(object):
            zope.interface.implements(Schema)
            foo = "bar"

        form = Form(Context(), zope.publisher.browser.TestRequest())
        form.form_fields = zope.formlib.form.FormFields(Schema)
        form.setUpWidgets()
        widget = form.widgets['foo']
        self.assertEllipsis('...cms:charlimit="70"...', widget())

    def test_charlimit_falls_back_to_max_length(self):

        class Schema(zope.interface.Interface):
            foo = zope.schema.TextLine(max_length=70)

        class Context(object):
            zope.interface.implements(Schema)
            foo = "bar"

        form = Form(Context(), zope.publisher.browser.TestRequest())
        form.form_fields = zope.formlib.form.FormFields(Schema)
        form.setUpWidgets()
        widget = form.widgets['foo']
        self.assertEllipsis('...cms:charlimit="70"...', widget())
