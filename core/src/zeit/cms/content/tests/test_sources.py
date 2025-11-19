from unittest.mock import Mock
import importlib.resources

import lxml.etree
import pyramid_dogpile_cache2
import zope.interface

import zeit.cms.config
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing


class ExampleSource(zeit.cms.content.sources.XMLSource):
    attribute = 'id'

    def _get_tree(self):
        return lxml.etree.fromstring(
            """\
<items>
  <item id="one">One</item>
  <item id="two" available="zeit.cms.interfaces.ICMSContent">Two</item>
  <item id="three" available="zeit.cms.interfaces.IAsset">Three</item>
</items>
"""
        )


class UnresolveableSource(zeit.cms.content.sources.XMLSource):
    attribute = 'id'

    def _get_tree(self):
        return lxml.etree.fromstring(
            """\
<items>
  <item id="foo" available="foo.bar.IAintResolveable">Foo</item>
</items>
"""
        )


class XMLSourceTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_values_without_available_attribute_are_returned_for_all_contexts(self):
        source = ExampleSource().factory
        context = Mock()
        self.assertEqual(['one'], source.getValues(context))

    def test_values_are_only_available_if_context_provides_that_interface(self):
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

        zope.component.getGlobalSiteManager().registerUtility(
            IFoo, zeit.cms.content.interfaces.IAddableContent, 'IFoo'
        )
        self.assertIn(IFoo, list(zeit.cms.content.sources.AddableCMSContentTypeSource()(None)))

    def test_to_override_title_or_type_set_tagged_values_to_none(self):
        source = zeit.cms.content.sources.AddableCMSContentTypeSource()(None).factory

        class IFoo(zeit.cms.interfaces.ICMSContent):
            pass

        IFoo.setTaggedValue('zeit.cms.title', 'My Foo')
        IFoo.setTaggedValue('zeit.cms.type', 'foo')

        self.assertEqual('My Foo', source.getTitle(None, IFoo))
        self.assertEqual('foo', source.getToken(None, IFoo))

        class IBar(IFoo):
            pass

        IBar.setTaggedValue('zeit.cms.title', None)
        IBar.setTaggedValue('zeit.cms.type', None)

        self.assertEqual(str(IBar), source.getTitle(None, IBar))
        self.assertEqual(str(IBar), source.getToken(None, IBar))


class ProductSourceTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        source = zeit.cms.content.sources.PRODUCT_SOURCE
        self.values = list(source(None))

    def test_returns_product_objects(self):
        product = self.values[-1]
        self.assertEqual('ZEDE', product.id)
        self.assertEqual('Online', product.title)
        source = zeit.cms.content.sources.PRODUCT_SOURCE(None)
        self.assertEqual('1234abc', source.find('KINZ').vgwort_code)

    def test_zeit_has_zeit_magazin_as_dependent_products(self):
        for value in self.values:
            if value.id == 'ZEI':
                self.assertEqual('Zeit Magazin', value.dependent_products[0].title)

    def test_zeit_has_print_counter(self):
        self.assertEqual('ZEI', self.values[0].id)
        self.assertEqual('print', self.values[0].counter)

    def test_source_without_dependencies_has_empty_list_as_dependent_products(self):
        self.assertEqual([], self.values[1].dependent_products)

    def test_invalid_dependent_products_configuration_has_no_effect_on_product(self):
        for value in self.values:
            if value.id == 'BADDEPENDENCY':
                self.assertEqual([], value.dependent_products)
                break


# Cannot use /testcontent here, see `different_context_objects` below
@zope.interface.implementer(zeit.cms.content.interfaces.ICommonMetadata)
class FakeRessort:
    pass


class SubRessortSourceTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.source = zeit.cms.content.sources.SubRessortSource()

    def test_constrains_values_to_parent_value(self):
        fake = FakeRessort()
        source = self.source(fake)

        fake.ressort = 'Deutschland'
        self.assertEqual(
            ['Datenschutz', 'Integration', 'Joschka Fisher', 'Meinung'], sorted(list(source))
        )

        fake.ressort = None
        self.assertIn('Meinung', list(source))

    def test_same_child_value_can_exist_for_multiple_parents(self):
        fake = FakeRessort()
        source = self.source(fake)
        fake.ressort = 'Deutschland'
        self.assertIn('Meinung', list(source))
        fake.ressort = 'International'
        self.assertIn('Meinung', list(source))

    def test_invalid_value_returns_the_raw_value_as_title(self):
        self.assertEqual('Invalid', self.source.factory.getTitle(None, 'Invalid'))

    def test_works_with_different_context_objects(self):
        # There's some weird interaction between .browser.widget.SubNavigationUpdater
        # and the workflow in some forms regarding what is saved when, which lead
        # to somewhat strange edge case handling, see e.g. b21e631 and 261aacd
        # XXX It is unclear which of these cases are still relevant today.

        # ICMSContent does not constrain the values at all. This is apparently
        # relevant for not having to save the ressort before selecting a subressort
        source = self.source(self.repository['testcontent'])
        self.assertIn('US-Wahl', list(source))

        # Strings are treated as the parent value, even though the normal context
        # type is ICommonMetadata
        source = self.source('Deutschland')
        self.assertEqual(
            ['Datenschutz', 'Integration', 'Joschka Fisher', 'Meinung'], sorted(list(source))
        )

        # Objects that don't provide the interface still work somewhat
        self.assertEqual('Meinung', self.source.factory.getTitle(object(), 'Meinung'))


class PrintRessortTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_source_has_title(self):
        source = zeit.cms.content.sources.PRINT_RESSORT_SOURCE
        self.assertEqual('Chanson', source.factory.getTitle(None, 'Chancen'))


class SerieSourceTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_returns_series_objects(self):
        source = zeit.cms.content.sources.SerieSource()(None)
        items = sorted(list(source), key=lambda x: x.serienname)
        serie = items[0]
        self.assertEqual('Autotest', serie.title)
        self.assertEqual('zeitmagazin-autotest', serie.url)

    def test_does_not_break_on_nonexistent_values(self):
        source = zeit.cms.content.sources.SerieSource(None)
        context = None
        self.assertEqual(None, source.factory.getTitle(context, None))
        self.assertEqual(None, source.factory.getToken(context, None))


class FeatureToggleTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_allows_overriding_values(self):
        toggles = zeit.cms.content.sources.FeatureToggleSource()(None)
        toggles.factory.config_url = 'toggle'
        zeit.cms.config.set(
            'zeit.cms',
            'toggle',
            'file://%s/feature-toggle-grouped.xml' % importlib.resources.files('zeit.cms.content'),
        )
        self.assertFalse(toggles.find('example'))
        toggles.set('example')
        self.assertTrue(toggles.find('example'))
        toggles.unset('example')
        self.assertFalse(toggles.find('example'))

        toggles.set('example')
        pyramid_dogpile_cache2.clear()
        self.assertFalse(toggles.find('example'))
