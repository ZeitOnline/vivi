from zeit.cms.checkout.helper import checked_out
import lxml.etree
import lxml.objectify
import mock
import zeit.cms.testing
import zeit.content.modules.rawtext
import zeit.content.modules.testing
import zeit.content.text.embed


class EmbedParameters(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.modules.testing.ZCML_LAYER

    def setUp(self):
        super(EmbedParameters, self).setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>'))

    def test_provides_dict_access_to_xml_nodes(self):
        self.module.params['p1'] = 'val'
        self.assertEqual('val', self.module.params['p1'])
        self.assertEllipsis(
            '...<param id="p1">val</param>...',
            lxml.etree.tostring(self.module.xml))

    def test_provides_attribute_access_for_formlib(self):
        self.module.params.p1 = 'val'
        self.assertEqual('val', self.module.params.p1)

    def test_uses_separate_xml_nodes_for_different_items(self):
        self.module.params['p1'] = 'val1'
        self.module.params['p2'] = 'val2'
        self.module.params['p1'] = 'val1'
        self.assertEqual('val1', self.module.params['p1'])
        self.assertEqual(
            1, lxml.etree.tostring(self.module.xml).count('val1'))

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
                'source=zeit.cms.content.contentsource.cmsContentSource)}')

        module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>'))
        module.text_reference = self.repository['embed']
        module.params['ref'] = self.repository['testcontent']
        lxml.objectify.deannotate(module.xml, cleanup_namespaces=True)
        self.assertEllipsis(
            '<container>...<param id="ref">http://xml.zeit.de/testcontent'
            '</param></container>', lxml.etree.tostring(module.xml))
        self.assertEqual(self.repository['testcontent'], module.params['ref'])

    def test_no_value_set_uses_field_default(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = 'none'
        self.repository['embed'] = embed
        with checked_out(self.repository['embed']) as co:
            co.parameter_definition = '{"p": zope.schema.Bool(default=True)}'

        module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>'))
        module.text_reference = self.repository['embed']
        self.assertEqual(True, module.params['p'])


class EmbedCSS(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.modules.testing.ZCML_LAYER

    def setUp(self):
        super(EmbedCSS, self).setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            self.context, lxml.objectify.XML('<container/>'))
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
        self.assertEllipsis("""\
<style>
#mymodule one, .mymodule one { a: 1; b: 2 }
#mymodule two, .mymodule two, #mymodule three, .mymodule three { c: 3 }
</style>""", self.css(self.module))
