from mock import Mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
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
  <item id="three" available="zeit.cms.interfaces.IAsset">Three</item>
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

    def test_available_can_list_multiple_interfaces_separated_by_space(self):
        source = ExampleSource().factory
        context = Mock()
        zope.interface.alsoProvides(context, zeit.cms.interfaces.IAsset)
        self.assertEqual(['one', 'two', 'three'], source.getValues(context))


class AddableCMSContentTypeSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_includes_IAddableContent(self):
        class IFoo(zeit.cms.interfaces.ICMSContent):
            pass

        self.zca.patch_utility(
            IFoo, zeit.cms.content.interfaces.IAddableContent, 'IFoo')
        self.assertIn(
            IFoo,
            list(zeit.cms.content.sources.AddableCMSContentTypeSource()(None)))


class StorystreamReferenceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_resolves_reference_from_source_config(self):
        self.repository['storystream'] = ExampleContentType()
        with checked_out(self.repository['testcontent']) as co:
            co.storystreams = (zeit.cms.content.sources.StorystreamSource()(
                None).find('test'),)
        self.assertEqual(
            self.repository['storystream'],
            self.repository['testcontent'].storystreams[0].references)


class AccessSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_cms_ids_should_be_translatable_to_c1_ids(self):
        access_source = zeit.cms.content.sources.AccessSource().factory
        for node in access_source._get_tree().iterchildren('*'):
            assert access_source.translate_to_c1(node.get('id')) == (
                node.get('c1_id'))

    def test_non_translatable_ids_should_return_none(self):
        access_source = zeit.cms.content.sources.AccessSource().factory
        assert access_source.translate_to_c1('hrmpf') is None


class ProductSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        source = zeit.cms.content.sources.PRODUCT_SOURCE
        self.values = list(source(None))

    def test_zeit_has_zeit_magazin_as_dependent_products(self):
        for value in self.values:
            if value.id == "ZEI":
                self.assertEqual('Zeit Magazin', value.dependent_products[0]
                                 .title)

    def test_source_without_dependencies_has_empty_list_as_dependent_products(
            self):
        self.assertEqual([], self.values[1].dependent_products)

    def test_invalid_dependent_products_configuration_has_no_effect_on_product(
            self):
        for value in self.values:
            if value.id == "BADDEPENDENCY":
                self.assertEqual([], value.dependent_products)
                break


class PrintRessortTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_source_has_title(self):
        source = zeit.cms.content.sources.PRINT_RESSORT_SOURCE
        self.assertEqual("Chanson", source.factory.getTitle(None, 'Chancen'))


class SerieSourceTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_does_not_break_on_nonexistent_values(self):
        source = zeit.cms.content.sources.SerieSource(None)
        context = None
        self.assertEqual(None, source.factory.getTitle(context, None))
        self.assertEqual(None, source.factory.getToken(context, None))
