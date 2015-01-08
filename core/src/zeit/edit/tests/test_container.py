from persistent.interfaces import IPersistent
import lxml.objectify
import mock
import unittest
import zeit.edit.container
import zeit.edit.testing
import zeit.edit.tests.fixture
import zope.interface


class TestContainer(unittest.TestCase):

    def get_container(self):
        parent = mock.Mock()
        parent._p_changed = False
        zope.interface.alsoProvides(parent, IPersistent)

        class Container(zeit.edit.container.Base):
            def _add(self, item):
                pass

            def _delete(self, key):
                pass

            def _get_keys(self, node):
                return []
        return Container(parent, mock.Mock())

    def test_delitem_should_set_p_changed(self):
        container = self.get_container()
        del container['foo']
        self.assertTrue(container.__parent__._p_changed)

    def test_add_should_set_p_changed(self):
        container = self.get_container()
        item = mock.Mock()
        item.__name__ = 'item'
        container.add(item)
        self.assertTrue(container.__parent__._p_changed)

    def test_updateOrder_should_set_p_changed(self):
        container = self.get_container()
        container.updateOrder([])
        self.assertTrue(container.__parent__._p_changed)


class UnknownBlockTest(zeit.edit.testing.FunctionalTestCase):

    def test_no_factory_for_node_returns_UnknownBlock(self):
        xml = lxml.objectify.fromstring("""
        <container xmlns:cp="http://namespaces.zeit.de/CMS/cp">
          <block cp:type="block" cp:__name__="foo"/>
          <something cp:__name__="bar"/>
        </container>
        """)
        container = zeit.edit.tests.fixture.Container(mock.Mock(), xml)
        self.assertTrue(zeit.edit.interfaces.IUnknownBlock.providedBy(
            container['bar']))


class SliceTest(zeit.edit.testing.FunctionalTestCase):

    def test_foo(self):
        context = mock.Mock()
        zope.interface.alsoProvides(context, IPersistent)
        container = zeit.edit.tests.fixture.Container(
            context, lxml.objectify.fromstring('<container/>'))
        block_factory = zope.component.getAdapter(
            container, zeit.edit.interfaces.IElementFactory, 'block')
        blocks = [block_factory() for i in range(4)]
        expected = [blocks[0], blocks[1]]
        expected = [x.__name__ for x in expected]
        actual = [x.__name__ for x in container.slice(
            blocks[0].__name__, blocks[1].__name__)]
        self.assertEqual(expected, actual)
