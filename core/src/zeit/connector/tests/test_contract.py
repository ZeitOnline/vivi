from datetime import datetime, timedelta
from io import BytesIO

import pytz
import transaction
import zope.interface.verify

from zeit.connector.interfaces import (
    CopyError,
    DeleteProperty,
    LockedByOtherSystemError,
    LockingError,
    MoveError,
)
from zeit.connector.resource import Resource
from zeit.connector.testing import copy_inherited_functions
import zeit.connector.interfaces
import zeit.connector.testing


class ContractReadWrite:
    NS = 'http://namespaces.zeit.de/CMS/testing'

    def add_resource(self, name, **kw):
        r = self.get_resource(name, **kw)
        r = self.connector[r.id] = r
        transaction.commit()
        return r

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
        self.assertIn('http://xml.zeit.de/testing', self.connector)
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
        self.assertEqual([], self.listCollection('http://xml.zeit.de/testing'))
        self.add_resource('one')
        self.add_resource('two')
        self.assertEqual(
            [('one', 'http://xml.zeit.de/testing/one'), ('two', 'http://xml.zeit.de/testing/two')],
            sorted(self.listCollection('http://xml.zeit.de/testing')),
        )

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
        collection = Resource(None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
        collection_2 = Resource(None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
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
        collection = Resource(None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.add_resource('folder/file')
        self.assertEqual(
            ['file'], [x[0] for x in self.listCollection('http://xml.zeit.de/testing/folder')]
        )
        # Re-adding a collection is a no-op
        collection = Resource(None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
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
        self.assertEqual(
            ['target'], [x[0] for x in self.listCollection('http://xml.zeit.de/testing')]
        )
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
        zeit.connector.testing.mkdir(self.connector, 'http://xml.zeit.de/testing/source')
        zeit.connector.testing.mkdir(self.connector, 'http://xml.zeit.de/testing/target')
        with self.assertRaises(MoveError):
            self.connector.move(
                'http://xml.zeit.de/testing/source', 'http://xml.zeit.de/testing/target'
            )

    def test_move_collection_applies_to_all_children(self):
        zeit.connector.testing.mkdir(self.connector, 'http://xml.zeit.de/testing/source')
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
        items = self.listCollection('http://xml.zeit.de/testing')
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
        zeit.connector.testing.mkdir(self.connector, 'http://xml.zeit.de/testing/source')
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
        zeit.connector.testing.mkdir(self.connector, 'http://xml.zeit.de/testing/target')
        with self.assertRaises(CopyError):
            self.connector.copy('http://xml.zeit.de/testing', 'http://xml.zeit.de/testing/target')


class ContractLock:
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
        zeit.connector.testing.mkdir(self.connector, collection_id)
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
        collection = Resource(None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
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

    def test_add_must_not_write_to_locked_unique_id(self):
        res = self.add_resource('foo')
        self.connector.lock(res.id, 'zope.external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.add(self.get_resource('foo'))

    def test_setitem_must_not_write_on_locked_object(self):
        res = self.get_resource('foo', body=b'one')
        self.connector['http://xml.zeit.de/testing/foo'] = res
        self.connector.lock(res.id, 'external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        res = self.get_resource('foo', body=b'nope')
        with self.assertRaises(LockedByOtherSystemError):
            self.connector['http://xml.zeit.de/testing/foo'] = res

    def test_set_property_on_own_lock_resources(self):
        uid = self.add_resource('foo', properties={('bar', self.NS): 'bar'}).id
        self.connector.lock(uid, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        self.connector.changeProperties(
            'http://xml.zeit.de/testing/foo',
            {('bar', self.NS): 'foo'},
        )
        transaction.commit()

    def test_copy_locked_resource(self):
        uid = self.add_resource('foo', properties={('bar', self.NS): 'bar'}).id
        self.connector.lock(uid, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        self.connector.copy('http://xml.zeit.de/testing/foo', 'http://xml.zeit.de/testing/target')
        transaction.commit()
        (principal, _, my_lock) = self.connector.locked('http://xml.zeit.de/testing/foo')
        self.assertEqual((principal, my_lock), ('zope.user', True))
        self.assertEqual(
            self.connector.locked('http://xml.zeit.de/testing/target'), (None, None, False)
        )

    def test_move_locked_resource_raises(self):
        uid = self.add_resource('foo', properties={('bar', self.NS): 'bar'}).id
        self.connector.lock(uid, 'zope.external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.move(uid, 'http://xml.zeit.de/testing/target')

    def test_delete_locked_resource_raises(self):
        uid = self.add_resource('foo', properties={('bar', self.NS): 'bar'}).id
        self.connector.lock(uid, 'zope.external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        (principal, _, my_lock) = self.connector.locked('http://xml.zeit.de/testing/foo')
        self.assertEqual((principal, my_lock), ('zope.external', False))
        with self.assertRaises(LockedByOtherSystemError):
            del self.connector['http://xml.zeit.de/testing/foo']

    def test_delete_own_lock_resource(self):
        uid = self.add_resource('foo', properties={('bar', self.NS): 'bar'}).id
        self.connector.lock(uid, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
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

    def test_changeProperties_on_locked_resource_raises(self):
        self.add_resource('foo', properties={('foo', self.NS): 'foo', ('bar', self.NS): 'bar'})
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('foo', res.properties[('foo', self.NS)])
        self.connector.lock(res.id, 'zope.external', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        with self.assertRaises(LockedByOtherSystemError):
            self.connector.changeProperties(
                'http://xml.zeit.de/testing/foo',
                {('foo', self.NS): 'qux', ('baz', self.NS): DeleteProperty},
            )


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
        if self.shortened_uuid:
            uuid = uuid.replace('{urn:uuid:', '').replace('}', '')
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


class ContractDAV(
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    zeit.connector.testing.ConnectorTest,
):
    shortened_uuid = False

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())


class ContractZopeDAV(
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    zeit.connector.testing.ConnectorTest,
):
    layer = zeit.connector.testing.ZOPE_CONNECTOR_LAYER
    shortened_uuid = False

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())


class ContractMock(
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    # ContractSearch,
    zeit.connector.testing.MockTest,
):
    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    # nyi copy_inherited_functions(ContractSearch, locals())

    def test_unlock_for_unknown_user_raises(self):
        """Not worth implementing for mock; no client (i.e. test in vivi) needs
        this behaviour.
        """


class ContractSQL(
    ContractReadWrite,
    ContractCopyMove,
    ContractLock,
    ContractSearch,
    zeit.connector.testing.SQLTest,
):
    shortened_uuid = True

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
