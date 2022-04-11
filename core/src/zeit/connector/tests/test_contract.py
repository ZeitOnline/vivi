from datetime import datetime, timedelta
from io import BytesIO
from zeit.connector.dav.interfaces import DAVNotFoundError
from zeit.connector.interfaces import CopyError, MoveError
from zeit.connector.resource import Resource
from zeit.connector.testing import copy_inherited_functions
import pytz
import transaction
import zeit.connector.interfaces
import zeit.connector.testing
import zope.interface.verify


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
        self.assertTrue(zope.interface.verify.verifyObject(
            zeit.connector.interfaces.IConnector, self.connector))

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
        self.add_resource(
            'foo', body='mybody', properties={('foo', self.NS): 'bar'})
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertTrue(zope.interface.verify.verifyObject(
            zeit.connector.interfaces.IResource, res))
        self.assertEqual('testing', res.type)
        self.assertEqual('http://xml.zeit.de/testing/foo', res.id)
        self.assertEqual('bar', res.properties[('foo', self.NS)])
        self.assertEqual(b'mybody', res.data.read())

    def test_listCollection_invalid_id_raises(self):
        with self.assertRaises(ValueError):
            self.listCollection('invalid')

    def test_listCollection_nonexistent_id_raises(self):
        with self.assertRaises(DAVNotFoundError):
            self.listCollection('http://xml.zeit.de/nonexistent')

    def test_listCollection_returns_name_uniqueId_pairs(self):
        self.assertEqual([], self.listCollection('http://xml.zeit.de/testing'))
        self.add_resource('one')
        self.add_resource('two')
        self.assertEqual(
            [('one', 'http://xml.zeit.de/testing/one'),
             ('two', 'http://xml.zeit.de/testing/two')],
            sorted(self.listCollection('http://xml.zeit.de/testing')))

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

    def test_delitem_removes_resource(self):
        res = self.add_resource('foo')
        self.assertIn(res.id, self.connector)
        del self.connector[res.id]
        transaction.commit()
        self.assertNotIn(res.id, self.connector)

    def test_delitem_collection_removes_children(self):
        collection = Resource(
            None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.add_resource('folder/file')
        del self.connector[collection.id + '/']  # XXX trailing slash DAV-ism
        transaction.commit()
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/folder']
        with self.assertRaises(KeyError):
            self.connector['http://xml.zeit.de/folder/file']

    def test_changeProperties_updates_properties(self):
        self.add_resource('foo', properties={
            ('foo', self.NS): 'foo',
            ('bar', self.NS): 'bar',
        })
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('foo', res.properties[('foo', self.NS)])
        self.connector.changeProperties(
            'http://xml.zeit.de/testing/foo', {('foo', self.NS): 'qux'})
        transaction.commit()
        res = self.connector['http://xml.zeit.de/testing/foo']
        self.assertEqual('qux', res.properties[('foo', self.NS)])
        self.assertEqual('bar', res.properties[('bar', self.NS)])

    def test_collection_is_determined_by_mime_type(self):
        # XXX This is the *only* place the mime type is still used, we should
        # think about removing it.
        collection = Resource(
            None, None, 'image', BytesIO(b''), None, 'httpd/unix-directory')
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.add_resource('folder/file')
        self.assertEqual(['file'], [x[0] for x in self.listCollection(
            'http://xml.zeit.de/testing/folder')])
        # Re-adding a collection is a no-op
        self.connector['http://xml.zeit.de/testing/folder'] = collection
        self.assertEqual(['file'], [x[0] for x in self.listCollection(
            'http://xml.zeit.de/testing/folder')])


class ContractCopyMove:

    def test_move_resource(self):
        self.add_resource(
            'source', body='mybody', properties={('foo', self.NS): 'bar'})
        self.connector.move(
            'http://xml.zeit.de/testing/source',
            'http://xml.zeit.de/testing/target')
        transaction.commit()
        self.assertEqual(['target'], [
            x[0] for x in self.listCollection('http://xml.zeit.de/testing')])
        res = self.connector['http://xml.zeit.de/testing/target']
        self.assertEqual('bar', res.properties[('foo', self.NS)])
        self.assertEqual(b'mybody', res.data.read())

    def test_move_to_existing_resource_overwrites(self):
        self.add_resource('source', properties={('foo', self.NS): 'bar'})
        self.add_resource('target')
        self.connector.move(
            'http://xml.zeit.de/testing/source',
            'http://xml.zeit.de/testing/target')
        transaction.commit()
        self.assertEqual(['target'], [
            x[0] for x in self.listCollection('http://xml.zeit.de/testing')])
        res = self.connector['http://xml.zeit.de/testing/target']
        self.assertEqual('bar', res.properties[('foo', self.NS)])

    def test_move_to_existing_differring_resource_raises(self):
        # Note that this currently cannot "really" occur, because
        # zeit.cms.repository.copypastemove uses INameChooser so the new name
        # is guaranteed to be unique.
        self.add_resource('source', body=b'one')
        self.add_resource('target', body=b'two')
        with self.assertRaises(MoveError):
            self.connector.move(
                'http://xml.zeit.de/testing/source',
                'http://xml.zeit.de/testing/target')

    def test_move_collection_to_existing_collection_raises(self):
        # I'm not sure this is actually desired behaviour.
        zeit.connector.testing.mkdir(
            self.connector, 'http://xml.zeit.de/testing/source')
        zeit.connector.testing.mkdir(
            self.connector, 'http://xml.zeit.de/testing/target')
        with self.assertRaises(MoveError):
            self.connector.move(
                'http://xml.zeit.de/testing/source',
                'http://xml.zeit.de/testing/target')

    def test_move_collection_applies_to_all_children(self):
        zeit.connector.testing.mkdir(
            self.connector, 'http://xml.zeit.de/testing/source')
        self.connector['http://xml.zeit.de/testing/source/file'] = Resource(
            None, None, 'text', BytesIO(b''))
        self.connector.move(
            'http://xml.zeit.de/testing/source',
            'http://xml.zeit.de/testing/target')
        self.assertNotIn(
            'http://xml.zeit.de/testing/source/file', self.connector)
        self.assertIn(
            'http://xml.zeit.de/testing/target/file', self.connector)

    def test_copy_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.connector.copy(
                'http://xml.zeit.de/nonexistent',
                'http://xml.zeit.de/testing/target')

    def test_copy_resource(self):
        self.add_resource(
            'source', body='mybody', properties={('foo', self.NS): 'bar'})
        self.connector.copy(
            'http://xml.zeit.de/testing/source',
            'http://xml.zeit.de/testing/target')
        transaction.commit()
        items = self.listCollection('http://xml.zeit.de/testing')
        self.assertEqual(['source', 'target'], sorted([x[0] for x in items]))
        for name, id in items:
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
                'http://xml.zeit.de/testing/source',
                'http://xml.zeit.de/testing/target')

    def test_copy_collection_applies_to_all_children(self):
        zeit.connector.testing.mkdir(
            self.connector, 'http://xml.zeit.de/testing/source')
        self.connector['http://xml.zeit.de/testing/source/file'] = Resource(
            None, None, 'text', BytesIO(b''))
        self.connector.copy(
            'http://xml.zeit.de/testing/source',
            'http://xml.zeit.de/testing/target')
        transaction.commit()
        self.assertIn(
            'http://xml.zeit.de/testing/source/file', self.connector)
        self.assertIn(
            'http://xml.zeit.de/testing/target/file', self.connector)

    def test_copy_collection_into_descendant_raises(self):
        zeit.connector.testing.mkdir(
            self.connector, 'http://xml.zeit.de/testing/target')
        with self.assertRaises(CopyError):
            self.connector.copy(
                'http://xml.zeit.de/testing',
                'http://xml.zeit.de/testing/target')


class ContractLock:

    def test_locked_shows_lock_status(self):
        id = self.add_resource('foo').id
        self.assertEqual((None, None, False), self.connector.locked(id))
        self.connector.lock(
            id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        user, until, mine = self.connector.locked(id)
        self.assertTrue(mine)
        self.assertEqual('zope.user', user)
        self.assertTrue(isinstance(until, datetime))

    def test_unlock_uses_locktoken_stored_in_connector(self):
        id = self.add_resource('foo').id
        lock = self.connector.lock(
            id, 'zope.user', datetime.now(pytz.UTC) + timedelta(hours=2))
        transaction.commit()
        unlock = self.connector.unlock(id)
        self.assertEqual((None, None, False), self.connector.locked(id))
        self.assertEqual(unlock, lock)


class ContractSearch:

    def test_search_unknown_metadata(self):
        from zeit.connector.search import SearchVar
        var = SearchVar('name', 'namespace')
        result = list(self.connector.search([var], var == 'foo'))
        assert result == []

    def test_search_known_metadata(self):
        from zeit.connector.search import SearchVar
        self.add_resource(
            'foo', body='mybody', properties={('foo', self.NS): 'foo'})
        self.add_resource(
            'bar', body='mybody', properties={('foo', self.NS): 'bar'})
        var = SearchVar('foo', self.NS)
        result = list(self.connector.search([var], var == 'foo'))
        assert result == [('http://xml.zeit.de/testing/foo', 'foo')]
        result = list(self.connector.search([var], var == 'bar'))
        assert result == [('http://xml.zeit.de/testing/bar', 'bar')]

    def test_search_and_operator(self):
        from zeit.connector.search import SearchVar
        self.add_resource(
            'foo', body='mybody', properties={
                ('foo', self.NS): 'foo'})
        self.add_resource(
            'bar', body='mybody', properties={
                ('foo', self.NS): 'bar',
                ('ham', self.NS): 'egg'})
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
        zeit.connector.testing.ConnectorTest):

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())


class ContractMock(
        ContractReadWrite,
        ContractCopyMove,
        ContractLock,
        # ContractSearch,
        zeit.connector.testing.MockTest):

    copy_inherited_functions(ContractReadWrite, locals())
    copy_inherited_functions(ContractCopyMove, locals())
    copy_inherited_functions(ContractLock, locals())
    # copy_inherited_functions(ContractSearch, locals())


class ContractSQL(
        ContractReadWrite,
        # ContractCopyMove,
        # ContractLock,
        ContractSearch,
        zeit.connector.testing.SQLTest):

    copy_inherited_functions(ContractReadWrite, locals())
    # copy_inherited_functions(ContractCopyMove, locals())
    # copy_inherited_functions(ContractLock, locals())
    copy_inherited_functions(ContractSearch, locals())
