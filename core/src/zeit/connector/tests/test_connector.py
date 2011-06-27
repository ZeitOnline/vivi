# coding: utf8
# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Connector test setup."""

from zeit.connector.interfaces import UUID_PROPERTY
import StringIO
import mock
import transaction
import zeit.connector.testing


class TestUnicode(zeit.connector.testing.ConnectorTest):

    def test_access(self):
        r = self.connector[
            u'http://xml.zeit.de/online/2007/09/laktose-milchzucker-gewöhnung']

    def test_create_and_list(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.assertEquals(
            [(u'ünicöde', rid)],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))

    def test_overwrite(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/testing/ünicöde'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Paff'),
            contentType='text/plain')
        self.assertEquals('Paff', self.connector[rid].data.read())

    def test_copy(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/testing/ünicöde'
        new_rid = rid + u'-copied'
        self.connector[rid] = zeit.connector.resource.Resource(

            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector.copy(rid, new_rid)
        resource = self.connector[new_rid]
        self.assertEquals('Pop.', resource.data.read())

    def test_move(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/testing/ünicöde'
        new_rid = rid + u'-renamed'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector.move(rid, new_rid)
        resource = self.connector[new_rid]
        self.assertEquals('Pop.', resource.data.read())


class TestEscaping(zeit.connector.testing.ConnectorTest):

    def test_hash(self):
        import zeit.connector.resource
        rid = 'http://xml.zeit.de/testing/foo#bar'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        resource = self.connector[rid]
        self.assertEquals('Pop.', resource.data.read())


class TestConflictDetectionBase(object):

    def setUp(self):
        super(TestConflictDetectionBase, self).setUp()
        rid = u'http://xml.zeit.de/testing/conflicting'
        self.connector[rid] = self.get_resource('conflicting', 'Pop.')
        r_a = self.connector[rid]
        self.r_a = self.get_resource(r_a.__name__, r_a.data.read(),
                                     r_a.properties)

        bang = self.get_resource('conflicting', 'Bang.')
        bang.properties[UUID_PROPERTY] = self.connector[rid].properties[
            UUID_PROPERTY]
        self.connector[rid] = bang

    def test_conflict(self):
        self.assertRaises(
            zeit.connector.dav.interfaces.PreconditionFailedError,
            self.connector.add, self.r_a)
        self.assertEquals(
            (None, None, False),
            self.connector.locked(self.r_a.id))

    def test_implicit_override(self):
        del self.r_a.properties[('getetag', 'DAV:')]
        self.connector.add(self.r_a)
        self.assertEquals('Pop.', self.connector[self.r_a.id].data.read())

    def test_explicit_override(self):
        self.connector.add(self.r_a, verify_etag=False)
        self.assertEquals('Pop.', self.connector[self.r_a.id].data.read())

    def test_adding_with_etag_fails(self):
        r = self.get_resource('cannot-be-added', '*Puff*')
        r.properties[('getetag', 'DAV:')] = 'schnutzengrutz'
        self.assertRaises(
            zeit.connector.dav.interfaces.PreconditionFailedError,
            self.connector.add, r)

    def test_no_conflict_with_same_content(self):
        self.r_a.data = StringIO.StringIO('Bang.')
        self.connector.add(self.r_a)
        self.assertEquals('Bang.', self.connector[self.r_a.id].data.read())


class TestConflictDetectionReal(
    TestConflictDetectionBase,
    zeit.connector.testing.ConnectorTest):

    pass

class TestConflictDetectionMock(
    TestConflictDetectionBase,
    zeit.connector.testing.MockTest):
    pass


class TestResource(zeit.connector.testing.ConnectorTest):

    def test_properties_should_be_current(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/testing/aresource'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain',
            properties={('foo', 'bar'): 'baz'})
        res = self.connector[rid]
        self.assertEquals('baz', res.properties[('foo', 'bar')])
        self.connector.changeProperties(
            rid, {('foo', 'bar'): 'changed'})
        self.assertEquals('changed', res.properties[('foo', 'bar')])


class TestConnectorCache(zeit.connector.testing.ConnectorTest):

    rid = 'http://xml.zeit.de/testing/cache_test'

    def setUp(self):
        import zeit.connector.resource
        super(TestConnectorCache, self).setUp()
        self.connector[self.rid] = zeit.connector.resource.Resource(
            self.rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        list(self.connector.listCollection('http://xml.zeit.de/testing/'))

    def test_deleting_non_existing_resource_does_not_create_cache_entry(self):
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/testing/']
        children.remove(self.rid)
        del self.connector[self.rid]
        self.assertEqual([], list(children))
        self.assertEqual(None, self.connector.property_cache.get(self.rid))

    def test_delete_updates_cache(self):
        del self.connector[self.rid]
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/testing/']
        self.assertEquals([], list(children))

    def test_cache_time_is_not_stored_on_dav(self):
        key = ('cached-time', 'INTERNAL')
        properties = self.connector[self.rid].properties
        cache_time = properties[key]
        self.connector.changeProperties(self.rid, {key: 'foo'})
        properties = self.connector[self.rid].properties
        self.assertNotEqual('foo', properties[key])
        davres = self.connector._get_dav_resource(self.rid)
        davres.update()
        self.assertTrue(key not in davres.get_all_properties())
        properties = self.connector[self.rid].properties
        self.assertEqual(cache_time, properties[key])

    def test_cache_time_is_not_stored_on_dav_with_add(self):
        key = ('cached-time', 'INTERNAL')
        self.connector.add(self.connector[self.rid])
        davres = self.connector._get_dav_resource(self.rid)
        davres.update()
        self.assertTrue(key not in davres.get_all_properties())

    def test_cache_handles_webdav_keys(self):
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        self.connector.changeProperties(self.rid, {key: 'baz'})

    def test_cache_handles_security_proxied_webdav_keys(self):
        import zope.security.proxy
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        key = zope.security.proxy.ProxyFactory(key)
        self.connector.changeProperties(self.rid, {key: 'baz'})

    def test_cache_does_not_store_security_proxied_webdav_keys(self):
        import zope.security.proxy
        key = zeit.connector.cache.WebDAVPropertyKey(('foo', 'bar'))
        key = zope.security.proxy.ProxyFactory(key)
        self.connector.property_cache['id'] = {key: 'baz'}
        self.assertTrue(isinstance(
            self.connector.property_cache['id'].keys()[0],
            zeit.connector.cache.WebDAVPropertyKey))

    def test_inconsistent_child_names_do_not_yields_non_existing_objects(self):
        self.assertEquals(
            [(u'cache_test', u'http://xml.zeit.de/testing/cache_test')],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))
        cache = self.connector.child_name_cache['http://xml.zeit.de/testing/']
        self.assertEquals(
            [u'http://xml.zeit.de/testing/cache_test'],
            list(cache))
        cache.add('http://xml.zeit.de/testing/cache_test_2')
        self.assertEquals(
            [(u'cache_test', u'http://xml.zeit.de/testing/cache_test')],
            list(self.connector.listCollection('http://xml.zeit.de/testing/')))

    def test_no_changes_should_not_cause_write(self):
        # Assign caches to DB to be able to detect changes.
        self.getRootFolder().property_cache = self.connector.property_cache
        self.getRootFolder().child_cache = self.connector.child_name_cache
        transaction.commit()

        jar = self.connector.property_cache._p_jar
        r = self.get_resource('res', 'Pop goes the weasel.')
        self.connector.add(r)
        list(self.connector.listCollection('http://xml.zeit.de/testing/'))
        # Two changes: property cache and child chache
        self.assertTrue(jar._registered_objects)
        transaction.commit()
        # No changes.
        self.assertEqual([], jar._registered_objects)
        self.connector.invalidate_cache(r.id)
        self.assertEqual([], jar._registered_objects)

    def test_invalidation_on_folder_with_non_folder_id_should_not_fail(self):
        self.connector.invalidate_cache('http://xml.zeit.de/testing')

    def test_invalidation_with_redirect_should_clear_old_location_cache(self):
        del self.connector.property_cache['http://xml.zeit.de/testing/']
        self.connector.property_cache['http://xml.zeit.de/testing'] = {
            ('foo', 'bar'): 'baz'}
        self.connector.child_name_cache['http://xml.zeit.de/testing'] = [
            'a', 'b', 'c']
        self.connector.invalidate_cache('http://xml.zeit.de/testing')
        self.assertEqual(
            None,
            self.connector.property_cache.get(
                'http://xml.zeit.de/testing'))
        self.assertEqual(
            'httpd/unix-directory',
            self.connector.property_cache[
                'http://xml.zeit.de/testing/'][('getcontenttype', 'DAV:')])
        self.assertEqual(
            None,
            self.connector.child_name_cache.get(
                'http://xml.zeit.de/testing'))
        self.assertEqual(
            [self.rid],
            list(self.connector.child_name_cache.get(
                'http://xml.zeit.de/testing/')))


class TestMove(zeit.connector.testing.ConnectorTest):

    def test_move_own_locked_resource_should_work(self):
        res = self.get_resource('foo', 'body')
        self.connector.add(res)
        self.connector.lock(res.id, 'userid', None)
        self.connector.move(res.id, 'http://xml.zeit.de/testing/bar')
        self.connector['http://xml.zeit.de/testing/bar']

    def test_move_locked_resource_should_raise(self):
        from zeit.connector.dav.interfaces import DAVLockedError
        res = self.get_resource('foo', 'body')
        self.connector.add(res)
        url = self.connector._id2loc(res.id)
        token = self.connector.get_connection().lock(
            url, owner='gimli', depth=0, timeout=20)
        try:
            self.assertRaises(
                DAVLockedError, lambda: self.connector.move(
                    res.id, 'http://xml.zeit.de/testing/bar'))
        finally:
            self.connector.unlock(res.id, token)

    def test_copy_locked_resource_should_work(self):
        res = self.get_resource('foo', 'body')
        self.connector.add(res)
        self.connector.lock(res.id, 'userid', None)
        self.connector.copy(res.id, 'http://xml.zeit.de/testing/bar')
        self.connector['http://xml.zeit.de/testing/bar']


class TestSearch(zeit.connector.testing.ConnectorTest):

    def test_should_raise_on_500(self):
        from zeit.connector.dav.interfaces import DAVError
        from zeit.connector.search import SearchVar
        var = SearchVar('name', 'namespace')
        result = self.connector.search([var], var == 'foo')
        with mock.patch(
            'zeit.connector.dav.davresource.DAVResult') as dav:
            dav.has_errors.return_value = True
            self.assertRaises(
                DAVError, lambda: result.next())
