from unittest import mock

import lxml.etree
import persistent.interfaces
import zope.component

from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture


class ElementUniqueIdTest(zeit.edit.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        xml = lxml.etree.fromstring(
            """
        <container
          xmlns:cp="http://namespaces.zeit.de/CMS/cp"
          cp:__name__="body">
            <block cp:type="block" cp:__name__="foo"/>
        </container>"""
        )
        content = self.repository['testcontent']
        self.container = zeit.edit.tests.fixture.Container(content, xml)
        self.block = zeit.edit.tests.fixture.Block(self.container, xml.find('block'))
        # Fake traversal ability.
        ExampleContentType.__getitem__ = lambda s, key: self.container

    def tearDown(self):
        del ExampleContentType.__getitem__
        super().tearDown()

    def test_block_ids_are_composed_of_parent_ids(self):
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body', self.container.uniqueId
        )
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body/' 'foo',
            self.block.uniqueId,
        )

    def test_resolving_block_ids_uses_traversal(self):
        block = zeit.cms.interfaces.ICMSContent(self.block.uniqueId)
        self.assertEqual(block, self.block)

    def test_block_without_name_uses_index(self):
        del self.block.xml.attrib['{http://namespaces.zeit.de/CMS/cp}__name__']
        with mock.patch('zeit.edit.tests.fixture.Container.index') as index:
            index.return_value = 0
            self.assertEqual(
                'http://block.vivi.zeit.de/http://xml.zeit.de' '/testcontent#body/0',
                self.block.uniqueId,
            )

    def test_block_equality_compares_xml(self):
        xml = """
        <container xmlns:cp="http://namespaces.zeit.de/CMS/cp">
            <block cp:type="block" cp:__name__="foo"/>
        </container>"""
        xml1 = lxml.etree.fromstring(xml)
        xml2 = lxml.etree.fromstring(xml)
        # CAUTION: xml1 == xml2 does not do what one might think it does,
        # thus block equality uses a proper in-depth xml comparison:
        self.assertNotEqual(xml1, xml2)
        block1 = zeit.edit.tests.fixture.Block(None, xml1)
        block2 = zeit.edit.tests.fixture.Block(None, xml2)
        self.assertEqual(block1, block2)

    def test_blocks_are_unequal_when_text_nodes_differ(self):
        # Upstream xmldiff wants to write to (a copy of) text nodes, which is
        # not possible with lxml.
        xml1 = lxml.etree.fromstring(
            """
        <container>
            <foo>bar</foo>
        </container>"""
        )
        xml2 = lxml.etree.fromstring(
            """
        <container>
            <foo>qux</foo>
        </container>"""
        )
        block1 = zeit.edit.tests.fixture.Block(None, xml1)
        block2 = zeit.edit.tests.fixture.Block(None, xml2)
        self.assertNotEqual(block1, block2)

    def test_blocks_are_unequal_when_tag_counts_differ(self):
        xml1 = lxml.etree.fromstring(
            """
        <foo><one/></foo>
        """
        )
        xml2 = lxml.etree.fromstring(
            """
        <foo><one/><two/><three/></foo>
        """
        )
        block1 = zeit.edit.tests.fixture.Block(None, xml1)
        block2 = zeit.edit.tests.fixture.Block(None, xml2)
        self.assertNotEqual(block1, block2)


class ElementFactoryTest(zeit.edit.testing.FunctionalTestCase):
    def test_factory_returns_interface_implemented_by_element(self):
        context = mock.Mock()
        zope.interface.alsoProvides(context, persistent.interfaces.IPersistent)
        container = zeit.edit.tests.fixture.Container(context, lxml.builder.E.container())
        block_factory = zope.component.getAdapter(
            container, zeit.edit.interfaces.IElementFactory, 'block'
        )
        self.assertEqual(zeit.edit.tests.fixture.IBlock, block_factory.provided_interface)
