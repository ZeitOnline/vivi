from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import lxml.objectify
import mock
import persistent.interfaces
import zeit.cms.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture
import zope.component


class ElementUniqueIdTest(zeit.edit.testing.FunctionalTestCase):

    def setUp(self):
        super(ElementUniqueIdTest, self).setUp()
        xml = lxml.objectify.fromstring("""
        <container
          xmlns:cp="http://namespaces.zeit.de/CMS/cp"
          cp:__name__="body">
            <block cp:type="block" cp:__name__="foo"/>
        </container>""")
        content = self.repository['testcontent']
        self.container = zeit.edit.tests.fixture.Container(content, xml)
        self.block = zeit.edit.tests.fixture.Block(
            self.container, xml.block)
        # Fake traversal ability.
        ExampleContentType.__getitem__ = lambda s, key: self.container

    def tearDown(self):
        del ExampleContentType.__getitem__
        super(ElementUniqueIdTest, self).tearDown()

    def test_block_ids_are_composed_of_parent_ids(self):
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body',
            self.container.uniqueId)
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body/'
            'foo',
            self.block.uniqueId)

    def test_resolving_block_ids_uses_traversal(self):
        block = zeit.cms.interfaces.ICMSContent(self.block.uniqueId)
        self.assertEqual(block, self.block)

    def test_block_without_name_uses_index(self):
        del self.block.xml.attrib['{http://namespaces.zeit.de/CMS/cp}__name__']
        with mock.patch('zeit.edit.tests.fixture.Container.index') as index:
            index.return_value = 0
            self.assertEqual(
                'http://block.vivi.zeit.de/http://xml.zeit.de'
                '/testcontent#body/0', self.block.uniqueId)

    def test_block_equality_compares_xml(self):
        xml1 = lxml.objectify.fromstring("""
        <container
          xmlns:cp="http://namespaces.zeit.de/CMS/cp"
          cp:__name__="body">
            <block cp:type="block" cp:__name__="foo"/>
        </container>""")
        xml2 = lxml.objectify.fromstring("""
        <container
          xmlns:cp="http://namespaces.zeit.de/CMS/cp"
          cp:__name__="body">
            <block cp:type="block" cp:__name__="foo"/>
        </container>""")
        # CAUTION: xml1 == xml2 does not do what you think it does,
        # thus block equality uses a proper in-depth xml comparison:
        self.assertNotEqual(xml1, xml2)
        block1 = zeit.edit.tests.fixture.Block(None, xml1)
        block2 = zeit.edit.tests.fixture.Block(None, xml2)
        self.assertEqual(block1, block2)


class ElementFactoryTest(zeit.edit.testing.FunctionalTestCase):

    def test_factory_returns_interface_implemented_by_element(self):
        context = mock.Mock()
        zope.interface.alsoProvides(context, persistent.interfaces.IPersistent)
        container = zeit.edit.tests.fixture.Container(
            context, lxml.objectify.fromstring('<container/>'))
        block_factory = zope.component.getAdapter(
            container, zeit.edit.interfaces.IElementFactory, 'block')
        self.assertEqual(
            zeit.edit.tests.fixture.IBlock, block_factory.provided_interface)
