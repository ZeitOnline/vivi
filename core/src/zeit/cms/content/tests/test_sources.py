from mock import Mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import gocept.lxml.objectify
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing
import zope.interface


class ExampleSource(zeit.cms.content.sources.XMLSource):

    attribute = 'id'

    def _get_tree(self):
        return gocept.lxml.objectify.fromstring("""\
<items>
  <item id="one">One</item>
  <item id="two" available="zeit.cms.interfaces.ICMSContent">Two</item>
</items>
""")


class UnresolveableSource(zeit.cms.content.sources.XMLSource):

    attribute = 'id'

    def _get_tree(self):
        return gocept.lxml.objectify.fromstring("""\
<items>
  <item id="foo" available="foo.bar.IAintResolveable">Foo</item>
</items>
""")


class XMLSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_values_without_available_attribute_are_returned_for_all_contexts(
            self):
        source = ExampleSource().factory
        context = Mock()
        self.assertEqual(['one'], source.getValues(context))

    def test_values_are_only_available_if_context_provides_that_interface(
            self):
        source = ExampleSource().factory
        context = Mock()
        zope.interface.alsoProvides(context, zeit.cms.interfaces.ICMSContent)
        self.assertEqual(['one', 'two'], source.getValues(context))

    def test_unresolveable_interfaces_should_make_item_unavailable(self):
        source = UnresolveableSource().factory
        context = Mock()
        self.assertEqual([], source.getValues(context))


class AddableCMSContentTypeSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_includes_IAddableContent(self):
        class IFoo(zeit.cms.interfaces.ICMSContent):
            pass

        self.zca.patch_utility(
            IFoo, zeit.cms.content.interfaces.IAddableContent, 'IFoo')
        self.assertIn(
            IFoo, list(zeit.cms.content.sources.AddableCMSContentTypeSource()))


class StorystreamReferenceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_resolves_reference_from_source_config(self):
        self.repository['storystream'] = TestContentType()
        with checked_out(self.repository['testcontent']) as co:
            co.storystreams = (zeit.cms.content.sources.StorystreamSource()(
                None).find('test'),)
        self.assertEqual(
            self.repository['storystream'],
            self.repository['testcontent'].storystreams[0].references)
