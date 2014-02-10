# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.testcontenttype.testcontenttype import TestContentType
import lxml.objectify
import mock
import zeit.cms.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture


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
        TestContentType.__getitem__ = lambda s, key: self.container

    def tearDown(self):
        del TestContentType.__getitem__
        super(ElementUniqueIdTest, self).tearDown()

    def test_block_ids_are_composed_of_parent_ids(self):
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body',
            self.container.uniqueId)
        self.assertEqual(
            'http://block.vivi.zeit.de/http://xml.zeit.de/testcontent#body/foo',
            self.block.uniqueId)

    def test_resolving_block_ids_uses_traversal(self):
        block = zeit.cms.interfaces.ICMSContent(self.block.uniqueId)
        # We can't compare instances, since Container creates a new instance on
        # each getitem.
        self.assertEqual(block.xml, self.block.xml)

    def test_block_without_name_uses_index(self):
        del self.block.xml.attrib['{http://namespaces.zeit.de/CMS/cp}__name__']
        with mock.patch('zeit.edit.tests.fixture.Container.index') as index:
            index.return_value = 0
            self.assertEqual(
                'http://block.vivi.zeit.de/http://xml.zeit.de'
                '/testcontent#body/0', self.block.uniqueId)
