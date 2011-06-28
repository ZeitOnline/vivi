# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest2 as unittest
import zope.interface


class TestContainer(unittest.TestCase):

    def get_container(self):
        from persistent.interfaces import IPersistent
        from zeit.edit.container import Base
        parent = mock.Mock()
        parent._p_changed = False
        zope.interface.alsoProvides(parent, IPersistent)
        class Container(Base):
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
