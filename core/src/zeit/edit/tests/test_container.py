from persistent.interfaces import IPersistent
from unittest import mock
import lxml.objectify
import unittest
import zeit.cms.workingcopy.interfaces
import zeit.edit.container
import zeit.edit.testing
import zeit.edit.tests.fixture
import zope.interface
import zope.security.proxy


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
        item.__parent__ = None
        container.add(item)
        self.assertTrue(container.__parent__._p_changed)

    def test_updateOrder_should_set_p_changed(self):
        container = self.get_container()
        container.updateOrder([])
        self.assertTrue(container.__parent__._p_changed)


class UnknownBlockTest(zeit.edit.testing.FunctionalTestCase):
    def test_no_factory_for_node_returns_UnknownBlock(self):
        xml = lxml.objectify.fromstring(
            """
        <container xmlns:cp="http://namespaces.zeit.de/CMS/cp">
          <block cp:type="block" cp:__name__="foo"/>
          <something cp:__name__="bar"/>
        </container>
        """
        )
        container = zeit.edit.tests.fixture.Container(mock.Mock(), xml)
        self.assertTrue(zeit.edit.interfaces.IUnknownBlock.providedBy(container['bar']))


class ContainerTest(zeit.edit.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        zope.interface.alsoProvides(self.context, IPersistent)
        self.container = zeit.edit.tests.fixture.Container(
            self.context, lxml.objectify.fromstring('<container/>')
        )

    def test_slice(self):
        blocks = [self.container.create_item('block') for i in range(4)]
        expected = [blocks[0], blocks[1]]
        expected = [x.__name__ for x in expected]
        actual = [x.__name__ for x in self.container.slice(blocks[0].__name__, blocks[1].__name__)]
        self.assertEqual(expected, actual)

    def test_get_recursive_finds_item_in_self(self):
        block = self.container.create_item('block')
        self.assertEqual(block, self.container.get_recursive(block.__name__))

    def test_get_recursive_finds_item_in_child_container(self):
        other = self.container.create_item('container')
        block = other.create_item('block')
        self.assertEqual(block, self.container.get_recursive(block.__name__))

    def test_moving_item_between_containers_sends_event(self):
        check_move = mock.Mock()
        zope.component.getGlobalSiteManager().registerHandler(
            check_move, (zeit.edit.interfaces.IBlock, zope.lifecycleevent.IObjectMovedEvent)
        )
        block = self.container.create_item('block')
        other = zeit.edit.tests.fixture.Container(
            self.context, lxml.objectify.fromstring('<container/>')
        )
        del self.container[block.__name__]
        other.add(block)
        self.assertTrue(check_move.called)

    def test_moved_item_has_new_parent(self):
        # Annoying mechanics gymnastics to check that security works.
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
        self.container.__parent__ = wc
        other = zeit.edit.tests.fixture.Container(wc, lxml.objectify.fromstring('<container/>'))
        block = self.container.create_item('block')
        del self.container[block.__name__]
        wrapped = zope.security.proxy.ProxyFactory(block)
        other.add(wrapped)
        # Since we don't retrieve block from other, this actually checks that
        # __parent__ was changed.
        self.assertEqual(other, block.__parent__)

    def test_getitem_with_int_uses_position(self):
        block = self.container.create_item('block')
        self.assertEqual(block, self.container[0])
        with self.assertRaises(KeyError):
            self.container[1]
