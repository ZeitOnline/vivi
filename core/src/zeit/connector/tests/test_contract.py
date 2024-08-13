from contextlib import contextmanager
from datetime import datetime, timedelta
from io import BytesIO
from unittest import mock
import collections.abc
import time

import pytz
import transaction
import zope.interface.verify

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.connector.interfaces import (
    CopyError,
    DeleteProperty,
    LockedByOtherSystemError,
    LockingError,
    MoveError,
)
from zeit.connector.resource import Resource
from zeit.connector.testing import ROOT, copy_inherited_functions
import zeit.cms.config
import zeit.connector.interfaces
import zeit.connector.testing


class ContractReadWrite:
    NS = 'http://namespaces.zeit.de/CMS/testing'

    def listCollection(self, id):  # XXX Why is this a generator?
        return list(self.connector.listCollection(id))

    def test_connector_provides_interface(self):
        self.assertTrue(
            zope.interface.verify.verifyObject(zeit.connector.interfaces.IConnector, self.connector)
        )

    def test_getitem_nonexistent_id_raises(self):
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/nonexistent']

    def test_contains_checks_resource_existence(self):
        self.assertIn(ROOT, self.connector)
        self.assertNotIn('http://xml.zeit.de/nonexistent', self.connector)

    def test_delitem_nonexistent_id_raises(self):
        with self.assertRaises(KeyError):
            del self.connector['http://xml.zeit.de/nonexistent']

    def test_getitem_returns_resource(self):
        self.add_resource('foo', body='mybody', properties={('foo', self.NS): 'bar'})
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertTrue(
            zope.interface.verify.verifyObject(zeit.connector.interfaces.IResource, res)
        )
        self.assertEqual('testing', res.type)
        self.assertEqual('http://xml.zeit.de/testing/foo', res.id)
        self.assertEqual('bar', res.properties[('foo', self.NS)])
        self.assertEqual(b'mybody', res.data.read())

    def test_listCollection_invalid_id_raises(self):
        with self.assertRaises(ValueError):
            self.listCollection('invalid')

    def test_listCollection_nonexistent_id_raises(self):
        with self.assertRaises(KeyError):
            self.listCollection('http://xml.zeit.de/nonexistent')

    def test_listCollection_returns_name_uniqueId_pairs(self):
        self.assertEqual([], self.listCollection(ROOT))
        self.add_resource('one')
        self.add_resource('two')
        self.assertEqual(
            [('one', 'http://xml.zeit.de/testing/one'), ('two', 'http://xml.zeit.de/testing/two')],
            sorted(self.listCollection(ROOT)),
        )

    def test_listCollection_works_for_root_folder(self):
        self.assertIn(
            ('testing', self.id_for_folder(ROOT)),
            self.listCollection('http://xml.zeit.de/'),
        )

    def test_getitem_works_for_root_folder(self):
        res = self.connector['http://xml.zeit.de/']
        self.assertEqual(self.folder_type, res.type)
        with self.assertNothingRaised():
            res.data.read()

    def test_setitem_stores_ressource(self):
        # Note: We're also testing this implicitly, due to self.add_resource().
        res = self.get_resource('foo')
        self.connector['http://xml.zeit.de/testing/foo'] = res
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('testing', res.type)

    def test_setitem_overwrites_ressource(self):
        res = self.get_resource('foo', body=b'one')
        self.connector['http://xml.zeit.de/testing/foo'] = res
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual(b'one', res.data.read())

        res = self.get_resource('foo', body=b'two')
        self.connector['http://xml.zeit.de/testing/foo'] = res
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual(b'two', res.data.read())

    def test_setitem_preserves_existing_properties(self):
        res = self.get_resource('foo', properties={('foo', self.NS): 'foo'})
        self.connector['http://xml.zeit.de/testing/foo'] = res
        transaction.commit()
        res = self.get_resource('foo', properties={('bar', self.NS): 'bar'})
        self.connector['http://xml.zeit.de/testing/foo'] = res
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('foo', res.properties[('foo', self.NS)])
        self.assertEqual('bar', res.properties[('bar', self.NS)])

    def test_add_is_convenience_for_setitem(self):
        self.connector.add(self.get_resource('foo'))
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('testing', res.type)

    def test_setitem_prohibits_writing_root_object(self):
        res = self.get_resource('foo')
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/'] = res

    def test_delitem_removes_resource(self):
        res = self.add_resource('foo')
        self.assertIn(res.id, self.connector)
        del self.connector[res.id]
        transaction.commit()
        self.assertNotIn(res.id, self.connector)

    def test_delitem_collection_removes_children(self):
        collection = Resource(None, None, 'image', BytesIO(b''), None, is_collection=True)
        collection_2 = Resource(None, None, 'image', BytesIO(b''), None, is_collection=True)
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.connector['http://xml.zeit.de/testing/folder/subfolder'] = collection_2
        self.add_resource('folder/file')
        self.add_resource('folder/subfolder/file')
        del self.connector[collection.id + '/']  # XXX trailing slash DAV-ism
        transaction.commit()
        for resource in ['folder', 'folder/file', 'folder/subfolder', 'folder/subfolder/file']:
            with self.assertRaises(KeyError):
                self.connector['http://xml.zeit.de/testing/' + resource]

    def test_changeProperties_updates_properties(self):
        self.add_resource(
            'foo',
            properties={
                ('foo', self.NS): 'foo',
                ('bar', self.NS): 'bar',
                ('baz', self.NS): 'baz',
            },
        )
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('foo', res.properties[('foo', self.NS)])
        self.connector.changeProperties(
            'http://xml.zeit.de/testing/foo',
            {('foo', self.NS): 'qux', ('baz', self.NS): DeleteProperty},
        )
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('qux', res.properties[('foo', self.NS)])
        self.assertEqual('bar', res.properties[('bar', self.NS)])
        self.assertNotIn(('baz', self.NS), res.properties)

    def test_collection_is_determined_by_mime_type(self):
        # XXX This is the *only* place the mime type is still used, we should
        # think about removing it.
        collection = Resource(None, None, 'image', BytesIO(b''), None, is_collection=True)
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.add_resource('folder/file')
        self.assertEqual(
            ['file'], [x[0] for x in self.listCollection('http://xml.zeit.de/testing/folder')]
        )
        # Re-adding a collection is a no-op
        collection = Resource(None, None, 'image', BytesIO(b''), None, is_collection=True)
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.assertEqual(
            ['file'], [x[0] for x in self.listCollection('http://xml.zeit.de/testing/folder')]
        )


class ContractCopyMove:
    def test_move_resource(self):
        self.add_resource('source', body='mybody', properties={('foo', self.NS): 'bar'})
        self.connector.move(
            'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
        )
        transaction.commit()
        self.assertEqual(['target'], [x[0] for x in self.listCollection(ROOT)])
        res = self.connector['http://xml.zeit.de/testing/target']
        self.assertEqual('bar', res.properties[('foo', self.NS)])
        self.assertEqual(b'mybody', res.data.read())

    def test_move_to_existing_resource_raises(self):
        # Note that this currently cannot "really" occur, because
        # zeit.cms.repository.copypastemove uses INameChooser so the new name
        # is guaranteed to be unique.
        self.add_resource('source')
        self.add_resource('target')
        with self.assertRaises(MoveError):
            self.connector.move(
                'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
            )

    def test_move_collection_to_existing_collection_raises(self):
        # I'm not sure this is actually desired behaviour.
        source = self.mkdir('source')
        target = self.mkdir('target')
        with self.assertRaises(MoveError):
            self.connector.move(source.id, target.id)

    def test_move_collection_applies_to_all_children(self):
        self.mkdir('source')
        self.connector['http://xml.zeit.de/testing/source/file'] = Resource(
            None, None, 'text', BytesIO(b'')
        )
        self.connector.move(
            'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
        )
        self.assertNotIn('http://xml.zeit.de/testing/source/file', self.connector)
        self.assertIn('http://xml.zeit.de/testing/target/file', self.connector)

    def test_move_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.connector.move(
                'http://xml.zeit.de/nonexistent', 'http://xml.zeit.de/testing/target'
            )

    def test_copy_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.connector.copy(
                'http://xml.zeit.de/nonexistent', 'http://xml.zeit.de/testing/target'
            )

    def test_copy_resource(self):
        self.add_resource('source', body='mybody', properties={('foo', self.NS): 'bar'})
        self.connector.copy(
            'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
        )
        transaction.commit()
        items = self.listCollection(ROOT)
        self.assertEqual(['source', 'target'], sorted([x[0] for x in items]))
        for _name, id in items:
            res = self.connector[id]
            self.assertEqual('testing', res.type)
            self.assertEqual(id, res.id)
            self.assertEqual('bar', res.properties[('foo', self.NS)])
            self.assertEqual(b'mybody', res.data.read())

    def test_copy_to_already_existing_resource_raises(self):
        self.add_resource('source', body=b'one')
        self.add_resource('target', body=b'two')
        with self.assertRaises(CopyError):
            self.connector.copy(
                'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
            )

    def test_copy_collection_applies_to_all_children(self):
        self.mkdir('source')
        self.connector['http://xml.zeit.de/testing/source/file'] = Resource(
            None, None, 'text', BytesIO(b'')
        )
        self.connector.copy(
            'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
        )
        transaction.commit()
        self.assertIn('http://xml.zeit.de/testing/source/file', self.connector)
        self.assertIn('http://xml.zeit.de/testing/target/file', self.connector)

    def test_copy_collection_into_descendant_raises(self):
        target = self.mkdir('target')
        with self.assertRaises(CopyError):
            self.connector.copy(ROOT, target.id)


class ContractLock:
    def lock_resource(self, name, user, **kw):
        res = self.add_resource(name, **kw)
        self.connector.lock(res.id, user, datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()

    def test_lock_nonexistent_resource_raises(self):
        with self.assertRaises(KeyError):
            self.connector.lock('http://xml.zeit.de/testing/foo', '', datetime.now(pytz.UTC))

    def test_locked_shows_lock_status(self):
        id = self.add_resource('foo').id
        self.assertEqual((None, None, False), self.connector.locked(id))
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        user, until, mine = self.connector.locked(id)
        self.assertTrue(mine)
        self.assertEqual('zope.user', user)
        self.assertTrue(isinstance(until, datetime))

    def test_unlock_removes_lock(self):
        id = self.add_resource('foo').id
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        self.connector.unlock(id)
        self.assertEqual((None, None, False), self.connector.locked(id))

    def test_unlock_for_unknown_user_raises(self):
        id = self.add_resource('foo').id
        self.connector.lock(id, 'external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.unlock(id)

    def test_locking_already_locked_resource_by_same_user_raises(self):
        id = self.add_resource('foo').id
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockingError):
            self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))

    def test_locking_already_locked_resource_raises(self):
        id = self.add_resource('foo').id
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockingError):
            self.connector.lock(
                id, 'zope.another_user', datetime.now(pytz.UTC) + timedelta(hours=2)
            )

    def test_move_operation_removes_lock(self):
        id = self.add_resource('foo').id
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        self.connector.move(id, 'http://xml.zeit.de/testing/bar')
        transaction.commit()
        self.assertEqual(
            self.connector.locked('http://xml.zeit.de/testing/bar'), (None, None, False)
        )

    def test_move_collection_with_locked_child_raises(self):
        collection_id = 'http://xml.zeit.de/testing/source'
        file_id = f'{collection_id}/foo'
        self.mkdir(collection_id)
        self.connector[f'{collection_id}/foo'] = Resource(None, None, 'text', BytesIO(b''))
        transaction.commit()
        token = self.connector.lock(
            file_id, 'external', datetime.now(pytz.UTC) + timedelta(hours=2)
        )
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.move(collection_id, 'http://xml.zeit.de/testing/target')
        self.connector._unlock(file_id, token)

    def test_delitem_collection_raises_error_if_children_are_locked(self):
        self.assertEqual([], self.listCollection('http://xml.zeit.de/testing'))
        collection = Resource(None, None, 'image', BytesIO(b''), None, is_collection=True)
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.add_resource('folder/file')
        self.add_resource('folder/one')
        self.add_resource('two')
        token_1 = self.connector.lock(
            'http://xml.zeit.de/testing/folder/one',
            'external',
            datetime.now(pytz.UTC) + timedelta(hours=2),
        )
        self.connector.lock(
            'http://xml.zeit.de/testing/two',
            'zope.user',
            datetime.now(pytz.UTC) + timedelta(hours=2),
        )
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            del self.connector['http://xml.zeit.de/testing']
        self.connector._unlock('http://xml.zeit.de/testing/folder/one', token_1)
        self.connector.unlock('http://xml.zeit.de/testing/two')

    def test_add_on_foreign_locked_resource_raises(self):
        self.lock_resource('foo', user='external')
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.add(self.get_resource('foo'))

    def test_setitem_on_foreign_locked_resource_raises(self):
        self.lock_resource('foo', user='external', body=b'one')
        res = self.get_resource('foo', body=b'nope')
        with self.assertRaises(LockedByOtherSystemError):
            self.connector['http://xml.zeit.de/testing/foo'] = res

    def test_setitem_on_own_locked_resource(self):
        self.lock_resource('foo', user='zope.user', body=b'one')
        res = self.get_resource('foo', body=b'nope')
        self.connector['http://xml.zeit.de/testing/foo'] = res
        foo = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual(b'nope', foo.data.read())

    def test_change_property_on_own_lock_resources(self):
        self.lock_resource('foo', user='zope.user', properties={('bar', self.NS): 'bar'})
        self.connector.changeProperties(
            'http://xml.zeit.de/testing/foo',
            {('bar', self.NS): 'foo'},
        )
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('foo', res.properties[('bar', self.NS)])

    def test_copy_own_locked_resource(self):
        self.lock_resource('foo', user='zope.user')
        self.connector.copy('http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/target')
        transaction.commit()
        (principal, _, my_lock) = self.connector.locked('http://xml.zeit.de/testing/foo')
        self.assertEqual((principal, my_lock), ('zope.user', True))
        self.assertEqual(
            self.connector.locked('http://xml.zeit.de/testing/target'), (None, None, False)
        )

    def test_move_foreign_locked_resource_raises(self):
        self.lock_resource('foo', user='external')
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.move(
                'http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/target'
            )

    def test_delete_foreign_locked_resource_raises(self):
        self.lock_resource('foo', user='external')
        (principal, _, my_lock) = self.connector.locked('http://xml.zeit.de/testing/foo')
        self.assertEqual((principal, my_lock), ('external', False))
        with self.assertRaises(LockedByOtherSystemError):
            del self.connector['http://xml.zeit.de/testing/foo']

    def test_delete_own_lock_resource(self):
        self.lock_resource('foo', user='zope.user')
        (principal, _, my_lock) = self.connector.locked('http://xml.zeit.de/testing/foo')
        self.assertEqual((principal, my_lock), ('zope.user', True))
        del self.connector['http://xml.zeit.de/testing/foo']
        transaction.commit()
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/testing/foo']

    def test_delete_resource(self):
        self.add_resource('foo', properties={('bar', self.NS): 'bar'})
        del self.connector['http://xml.zeit.de/testing/foo']
        transaction.commit()
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/testing/foo']

    def test_changeProperties_on_foreign_locked_resource_raises(self):
        self.lock_resource(
            'foo', user='external', properties={('foo', self.NS): 'foo', ('bar', self.NS): 'bar'}
        )
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.changeProperties(
                'http://xml.zeit.de/testing/foo',
                {('foo', self.NS): 'qux', ('baz', self.NS): DeleteProperty},
            )

    def test_lock_timeout(self):
        id = self.add_resource('foo').id
        self.assertEqual((None, None, False), self.connector.locked(id))
        self.connector.lock(id, 'zope.user', datetime.now(pytz.UTC))
        transaction.commit()
        if 'DAV' in self.__class__.__name__:
            # dav needs some more time to unlock
            time.sleep(0.9)
        time.sleep(0.1)
        self.assertEqual((None, None, False), self.connector.locked(id))


class ContractSearch:
    def test_search_unknown_metadata(self):
        from zeit.connector.search import SearchVar

        var = SearchVar('name', 'namespace')
        result = list(self.connector.search([var], var == 'foo'))
        assert result == []

    def test_search_known_metadata(self):
        from zeit.connector.search import SearchVar

        self.add_resource('foo', body='mybody', properties={('foo', self.NS): 'foo'})
        self.add_resource('bar', body='mybody', properties={('foo', self.NS): 'bar'})
        var = SearchVar('foo', self.NS)
        result = list(self.connector.search([var], var == 'foo'))
        assert result == [('http://xml.zeit.de/testing/foo', 'foo')]
        result = list(self.connector.search([var], var == 'bar'))
        assert result == [('http://xml.zeit.de/testing/bar', 'bar')]

    def test_search_uuid(self):
        uuid = '{urn:uuid:deadbeef-dead-dead-dead-beefbeefbeef}'
        namespace = self.NS.replace('/testing', '/document')
        from zeit.connector.search import SearchVar

        self.add_resource('foo', body='mybody', properties={('uuid', namespace): uuid})
        var = SearchVar('uuid', namespace)
        result = list(self.connector.search([var], var == uuid))
        assert result == [('http://xml.zeit.de/testing/foo', uuid)]

    def test_search_and_operator(self):
        from zeit.connector.search import SearchVar

        self.add_resource('foo', body='mybody', properties={('foo', self.NS): 'foo'})
        self.add_resource(
            'bar', body='mybody', properties={('foo', self.NS): 'bar', ('ham', self.NS): 'egg'}
        )
        foo = SearchVar('foo', self.NS)
        ham = SearchVar('ham', self.NS)
        result = list(self.connector.search([ham], (foo == 'foo') & (ham == 'egg')))
        assert result == []
        result = list(self.connector.search([ham], (foo == 'bar') & (ham == 'egg')))
        assert result == [('http://xml.zeit.de/testing/bar', 'egg')]

        result = list(self.connector.search([foo, ham], (foo == 'bar') & (ham == 'egg')))
        assert result == [('http://xml.zeit.de/testing/bar', 'bar', 'egg')]


class NormalizeFolders(collections.abc.MutableMapping):
    """DAV connector requires trailing slash for uniqueId of folders, while SQL
    connector finally stopped exposing this implementation detail.
    To be able to talk to both, we need to normalize this, see the respective
    `Protocol` helper class.
    """

    def __init__(self, normalize, cache):
        self.normalize = normalize
        self.cache = cache

    def __getitem__(self, key):
        return list(self.cache[self.normalize(key)])

    def __setitem__(self, key, value):
        self.cache[self.normalize(key)] = value

    def __delitem__(self, key):
        del self.cache[self.normalize(key)]

    def __iter__(self):
        return [self.normalize(x) for x in self.cache.keys()]

    def __len__(self):
        return len(self.cache)


class ContractCache:
    @property
    def child_name_cache(self):
        return NormalizeFolders(self.id_for_folder, self.connector.child_name_cache)

    def test_setitem_populates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        self.assertEqual('foo', self.connector.property_cache[res.id][prop])

    def test_setitem_updates_parent_child_name_cache(self):
        res = self.add_resource('foo')
        self.assertEqual([res.id], self.child_name_cache[ROOT])

    def test_setitem_collection_populates_child_name_cache(self):
        folder = 'http://xml.zeit.de/testing/foo'
        self.assertNotIn(folder, self.child_name_cache)
        self.mkdir(folder)
        self.assertEqual([], self.child_name_cache[folder])

    def test_setitem_removes_body_cache(self):
        res = self.add_resource('foo', body=b'foo')
        self.connector[res.id].data
        self.assertTrue(self.has_body_cache(res.id))
        self.connector.add(res)
        self.assertFalse(self.has_body_cache(res.id))

    def test_getitem_populates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        del self.connector.property_cache[res.id]
        res = self.connector[res.id]
        self.assertEqual('foo', self.connector.property_cache[res.id][prop])

    def test_resource_read_populates_body_cache(self):
        res = self.add_resource('foo', body=b'foo')
        self.connector[res.id].data
        self.assertEqual(b'foo', self.connector.body_cache[res.id].read())

    def test_listCollection_populates_child_name_cache(self):
        del self.child_name_cache[ROOT]
        self.assertEqual([], self.listCollection(ROOT))
        self.assertEqual([], self.child_name_cache[ROOT])

    def test_changeProperties_updates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        self.connector.changeProperties(res.id, {prop: 'bar'})
        self.assertEqual('bar', self.connector.property_cache[res.id][prop])

    def test_delitem_removes_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        del self.connector[res.id]
        self.assertNotIn(res.id, self.connector.property_cache)

    def test_delitem_removes_from_child_name_cache(self):
        res = self.add_resource('foo')
        self.assertIn(res.id, self.child_name_cache[ROOT])
        del self.connector[res.id]
        self.assertNotIn(res.id, self.child_name_cache[ROOT])

    def test_delitem_collection_removes_child_name_cache(self):
        folder = self.mkdir('foo')
        del self.connector[folder.id]
        self.assertNotIn(folder.id, self.child_name_cache)

    def test_delitem_removes_body_cache(self):
        res = self.add_resource('foo', body=b'foo')
        self.connector[res.id].data
        self.assertTrue(self.has_body_cache(res.id))
        del self.connector[res.id]
        self.assertFalse(self.has_body_cache(res.id))

    def test_copy_populates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        new = 'http://xml.zeit.de/testing/bar'
        self.connector.copy(res.id, new)
        self.assertEqual('foo', self.connector.property_cache[new][prop])

    def test_copy_updates_parent_child_name_cache(self):
        res = self.add_resource('foo')
        new = 'http://xml.zeit.de/testing/bar'
        self.connector.copy(res.id, new)
        self.assertIn('http://xml.zeit.de/testing/bar', self.child_name_cache[ROOT])

    def test_copy_collection_populates_child_name_cache(self):
        self.mkdir('foo')
        self.connector.copy('http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/bar')
        self.assertEqual([], self.child_name_cache['http://xml.zeit.de/testing/bar'])

    def test_copy_nonempty_collection_populates_child_name_cache(self):
        self.mkdir('foo')
        self.add_resource('foo/qux')
        self.connector.copy('http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/bar')
        self.assertEqual(
            ['http://xml.zeit.de/testing/bar/qux'],
            self.child_name_cache['http://xml.zeit.de/testing/bar'],
        )

    def test_move_updates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        new = 'http://xml.zeit.de/testing/bar'
        self.connector.move(res.id, new)
        self.assertNotIn(res.id, self.connector.property_cache)
        self.assertEqual('foo', self.connector.property_cache[new][prop])

    def test_move_updates_parent_child_name_cache(self):
        res = self.add_resource('foo')
        self.connector.move(res.id, 'http://xml.zeit.de/testing/bar')
        self.assertEqual(['http://xml.zeit.de/testing/bar'], self.child_name_cache[ROOT])

    def test_move_collection_updates_child_name_cache(self):
        self.mkdir('foo')
        self.connector.move('http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/bar')
        self.assertNotIn('http://xml.zeit.de/testing/foo', self.child_name_cache)
        self.assertEqual([], self.child_name_cache['http://xml.zeit.de/testing/bar'])

    def test_move_removes_body_cache(self):
        res = self.add_resource('foo', body=b'foo')
        self.connector[res.id].data
        self.assertTrue(self.has_body_cache(res.id))
        self.connector.move(res.id, 'http://xml.zeit.de/testing/bar')
        self.assertFalse(self.has_body_cache(res.id))

    def test_when_storage_changed_invalidate_updates_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        self.change_properties_in_storage(res.id, {prop: 'bar'})
        transaction.commit()
        self.connector.invalidate_cache(res.id)
        self.assertEqual('bar', self.connector.property_cache[res.id][prop])

    def test_when_storage_deleted_invalidate_removes_property_cache(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        self.delete_in_storage(res.id)
        transaction.commit()
        self.connector.invalidate_cache(res.id)
        self.assertNotIn(res.id, self.connector.property_cache)

    def test_trigger_invalidate_via_event(self):
        prop = ('foo', self.NS)
        res = self.add_resource('foo', properties={prop: 'foo'})
        self.change_properties_in_storage(res.id, {prop: 'bar'})
        transaction.commit()
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(res.id))
        self.assertEqual('bar', self.connector.property_cache[res.id][prop])

    def test_when_storage_changed_invalidate_updates_child_name_cache(self):
        self.add_in_storage('foo')
        transaction.commit()
        self.connector.invalidate_cache(ROOT)
        self.assertEqual(['http://xml.zeit.de/testing/foo'], self.child_name_cache[ROOT])

    def test_when_storage_deleted_invalidate_removes_child_name_cache(self):
        res = self.add_resource('foo')
        self.delete_in_storage(res.id)
        transaction.commit()
        self.connector.invalidate_cache(res.id)
        self.assertEqual([], self.child_name_cache[ROOT])

    def test_invalidate_removes_body_cache(self):
        res = self.add_resource('foo', body=b'foo')
        self.connector[res.id].data
        self.assertTrue(self.has_body_cache(res.id))
        self.change_body_in_storage(res.id, b'bar')
        transaction.commit()
        self.connector.invalidate_cache(res.id)
        self.assertFalse(self.has_body_cache(res.id))

    def test_getitem_twice_returns_cached_result(self):
        res = self.add_resource('foo')

        def get(uniqueid):
            res = self.connector[uniqueid]
            res.properties
            res.data

        get(res.id)
        transaction.commit()
        with self.disable_storage():
            with self.assertNothingRaised():
                get(res.id)

    def test_listCollection_twice_returns_cached_result(self):
        res = self.mkdir('foo')
        self.listCollection(res.id)
        transaction.commit()
        with self.disable_storage():
            with self.assertNothingRaised():
                self.listCollection(res.id)

    def test_locked_returns_cached_result(self):
        res = self.add_resource('foo')
        self.connector.lock(
            res.id,
            'zope.user',
            datetime.now(pytz.UTC) + timedelta(hours=2),
        )
        transaction.commit()
        with self.disable_storage():
            with self.assertNothingRaised():
                (principal, _, my_lock) = self.connector.locked(res.id)
                self.assertEqual('zope.user', principal)


class DAVProtocol:
    folder_type = 'collection'

    def id_for_folder(self, id):
        if not id.endswith('/'):
            id += '/'
        return id

    def change_properties_in_storage(self, uniqueid, properties):
        self.layer['connector'].changeProperties(uniqueid, properties)

    def change_body_in_storage(self, uniqueid, body):
        current = self.layer['connector'][uniqueid]
        res = Resource(
            current.id, current.__name__, current.type, BytesIO(body), current.properties
        )
        self.layer['connector'].add(res)

    def delete_in_storage(self, uniqueid):
        del self.layer['connector'][uniqueid]

    def add_in_storage(self, name):
        self.layer['connector'].add(self.get_resource(name))

    def has_body_cache(self, uniqueid):
        try:
            self.connector.body_cache.getData(
                uniqueid, self.connector.property_cache[uniqueid][('getetag', 'DAV:')]
            )
        except KeyError:
            return False
        else:
            return True

    @contextmanager
    def disable_storage(self):
        with mock.patch.object(self.connector, 'get_connection') as conn:
            conn.side_effect = RuntimeError('disabled')
            yield


class ContractDAV(
    DAVProtocol,
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    # ContractCache,
    zeit.connector.testing.ConnectorTest,
):
    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
    # not implemented copy_inherited_functions(ContractCache, locals())


class ContractZopeDAV(
    DAVProtocol,
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    ContractCache,
    zeit.connector.testing.ConnectorTest,
):
    layer = zeit.connector.testing.ZOPE_DAV_CONNECTOR_LAYER

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
    copy_inherited_functions(ContractCache, locals())


class ContractMock(
    DAVProtocol,
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    # ContractSearch,
    # ContractCache,
    zeit.connector.testing.MockTest,
):
    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    # not implemented copy_inherited_functions(ContractSearch, locals())
    # not implemented copy_inherited_functions(ContractCache, locals())

    def test_unlock_for_unknown_user_raises(self):
        """Not worth implementing for mock; no client (i.e. test in vivi) needs
        this behaviour.
        """


class SQLProtocol:
    folder_type = 'folder'

    def id_for_folder(self, id):
        return id

    def change_properties_in_storage(self, uniqueid, properties):
        content = self.connector._get_content(uniqueid)
        current = content.to_webdav()
        current.update(properties)
        content.from_webdav(current)

    def change_body_in_storage(self, uniqueid, body):
        content = self.connector._get_content(uniqueid)
        content.body = body

    def delete_in_storage(self, uniqueid):
        content = self.connector._get_content(uniqueid)
        self.connector.session.delete(content)

    def add_in_storage(self, name):
        from zeit.connector.postgresql import Content

        resource = self.get_resource(name)
        content = Content()
        content.from_webdav(resource.properties)
        content.type = resource.type
        content.is_collection = resource.is_collection
        (content.parent_path, content.name) = self.connector._pathkey(resource.id)
        self.connector.session.add(content)

    def has_body_cache(self, uniqueid):
        return uniqueid in self.connector.body_cache

    @contextmanager
    def disable_storage(self):
        original = self.connector.session
        self.connector.session = mock.Mock(side_effect=RuntimeError('disabled'))
        yield
        self.connector.session = original


class ContractSQL(
    SQLProtocol,
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    # ContractCache,
    zeit.connector.testing.SQLTest,
):
    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
    # not implemented copy_inherited_functions(ContractCache, locals())


class ContractZopeSQL(
    SQLProtocol,
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    ContractCache,
    zeit.connector.testing.ZopeSQLTest,
):
    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
    copy_inherited_functions(ContractCache, locals())


class ContractProperties:
    def setUp(self):
        super().setUp()
        zeit.cms.config.set('zeit.connector', 'read_metadata_columns', 'True')
        zeit.cms.config.set('zeit.connector', 'write_metadata_columns', 'True')
        self.repository['testcontent'] = ExampleContentType()

    def tearDown(self):
        zeit.cms.config.set('zeit.connector', 'read_metadata_columns', 'False')
        zeit.cms.config.set('zeit.connector', 'write_metadata_columns', 'False')
        super().tearDown()

    def test_converts_scalar_types_on_read(self):
        self.repository.connector.changeProperties(
            'http://xml.zeit.de/testcontent',
            {('overscrolling', 'http://namespaces.zeit.de/CMS/document'): True},
        )
        self.assertIs(True, self.repository['testcontent'].overscrolling)

    def test_converts_scalar_types_on_write(self):
        with checked_out(self.repository['testcontent']) as co:
            co.overscrolling = True
        resource = self.repository.connector['http://xml.zeit.de/testcontent']
        self.assertIs(
            True, resource.properties[('overscrolling', 'http://namespaces.zeit.de/CMS/document')]
        )


class PropertiesSQL(ContractProperties, zeit.cms.testing.FunctionalTestCase):
    layer = zeit.connector.testing.SQL_CONTENT_LAYER
    copy_inherited_functions(ContractProperties, locals())


class PropertiesMock(ContractProperties, zeit.cms.testing.FunctionalTestCase):
    layer = zeit.cms.testing.ZOPE_LAYER
    copy_inherited_functions(ContractProperties, locals())
