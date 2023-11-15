from unittest import mock
from zeit.cms.checkout.helper import checked_out
import lxml.etree
import lxml.objectify
import zeit.content.modules.rawtext
import zeit.content.modules.testing
import zeit.content.text.embed


class EmbedParameters(zeit.content.modules.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>')
        )

    def test_provides_dict_access_to_xml_nodes(self):
        self.module.params['p1'] = 'val'
        self.assertEqual('val', self.module.params['p1'])
        self.assertEllipsis(
            '...<param id="p1">val</param>...', lxml.etree.tostring(self.module.xml, encoding=str)
        )

    def test_provides_attribute_access_for_formlib(self):
        self.module.params.p1 = 'val'
        self.assertEqual('val', self.module.params.p1)

    def test_uses_separate_xml_nodes_for_different_items(self):
        self.module.params['p1'] = 'val1'
        self.module.params['p2'] = 'val2'
        self.module.params['p1'] = 'val1'
        self.assertEqual('val1', self.module.params['p1'])
        self.assertEqual(1, zeit.cms.testing.xmltotext(self.module.xml).count('val1'))

    def test_setting_empty_value_removes_node(self):
        self.module.params['p1'] = 'val1'
        self.module.params['p1'] = None
        self.assertFalse(self.module.xml.xpath('//param'))

    def test_serializes_via_dav_converter(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        self.repository['embed'] = embed
        with checked_out(self.repository['embed']) as co:
            co.parameter_definition = (
                '{"ref": zope.schema.Choice('
                'source=zeit.cms.content.contentsource.cmsContentSource)}'
            )

        module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>')
        )
        module.text_reference = self.repository['embed']
        module.params['ref'] = self.repository['testcontent']
        lxml.objectify.deannotate(module.xml, cleanup_namespaces=True)
        self.assertEllipsis(
            '<container>...<param id="ref">http://xml.zeit.de/testcontent' '</param></container>',
            lxml.etree.tostring(module.xml, encoding=str),
        )
        self.assertEqual(self.repository['testcontent'], module.params['ref'])

    def test_no_value_set_uses_field_default(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        self.repository['embed'] = embed
        with checked_out(self.repository['embed']) as co:
            co.parameter_definition = '{"p": zope.schema.Bool(default=True)}'

        module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>')
        )
        module.text_reference = self.repository['embed']
        self.assertEqual(True, module.params['p'])

    def test_does_not_use_objectify_number_heuristics(self):
        self.module.params['p1'] = '10.000'
        self.assertEqual('10.000', self.module.params['p1'])


class EmbedCSS(zeit.content.modules.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>')
        )
        self.module.__name__ = 'mymodule'

    def css(self, module):
        return zeit.content.modules.rawtext.ICSS(module).vivi_css

    def test_no_css_set_returns_none(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        self.repository['embed'] = embed
        self.module.text_reference = self.repository['embed']
        self.assertEqual(None, self.css(self.module))

    def test_selectors_are_prefixed_with_module_id(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        embed.vivi_css = """\
one { a: 1; b: 2; }
two, three { c: 3; }
"""
        self.repository['embed'] = embed
        self.module.text_reference = self.repository['embed']
        self.assertEllipsis(
            """\
<style>
#mymodule one, .mymodule one { a: 1; b: 2 }
#mymodule two, .mymodule two, #mymodule three, .mymodule three { c: 3 }
</style>""",
            self.css(self.module),
        )


class ConsentInfo(zeit.content.modules.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>')
        )

    def test_stores_local_values_in_xml(self):
        info = zeit.cmp.interfaces.IConsentInfo(self.module)
        info.has_thirdparty = True
        info.thirdparty_vendors = ['twitter', 'facebook']
        self.assertEqual(True, info.has_thirdparty)
        self.assertEqual(('twitter', 'facebook'), info.thirdparty_vendors)
        self.assertEqual(('cmp-twitter', 'cmp-facebook'), info.thirdparty_vendors_cmp_ids)
        self.assertEqual(
            '<container has_thirdparty="yes"' ' thirdparty_vendors="twitter;facebook"/>',
            lxml.etree.tostring(self.module.xml, encoding=str),
        )

    def test_passes_through_referenced_values(self):
        info = zeit.cmp.interfaces.IConsentInfo(self.module)
        self.assertFalse(info.has_thirdparty)

        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        self.repository['embed'] = embed
        with checked_out(self.repository['embed']) as co:
            info = zeit.cmp.interfaces.IConsentInfo(co)
            info.has_thirdparty = True
            info.thirdparty_vendors = ['twitter', 'facebook']
        self.module.text_reference = self.repository['embed']

        info = zeit.cmp.interfaces.IConsentInfo(self.module)
        self.assertEqual(True, info.has_thirdparty)
        self.assertEqual(('twitter', 'facebook'), info.thirdparty_vendors)
