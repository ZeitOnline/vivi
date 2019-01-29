import lxml.etree
import lxml.objectify
import mock
import zeit.cms.testing
import zeit.content.modules.rawtext
import zeit.content.modules.testing


class EmbedParameters(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.modules.testing.ZCML_LAYER

    def setUp(self):
        super(EmbedParameters, self).setUp()
        context = mock.Mock()
        context.__parent__ = None
        self.module = zeit.content.modules.rawtext.RawText(
            context, lxml.objectify.XML('<container/>'))

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
