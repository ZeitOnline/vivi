# coding: utf8
from zeit.connector.testing import copy_inherited_functions
import StringIO
import mock
import os
import transaction
import unittest
import zeit.connector.connector
import zeit.connector.interfaces
import zeit.connector.testing
import zope.component


class TestUnicode(zeit.connector.testing.ConnectorTest):

    def test_access(self):
        self.connector[
            u'http://xml.zeit.de/online/2007/09/laktose-milchzucker-gewöhnung']

    def test_create_and_list(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/%s/ünicöde' % self.layer.testfolder
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.assertEquals(
            [(u'ünicöde', rid)],
            list(self.connector.listCollection(
                'http://xml.zeit.de/%s/' % self.layer.testfolder)))

    def test_overwrite(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/%s/ünicöde' % self.layer.testfolder
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
        rid = u'http://xml.zeit.de/%s/ünicöde' % self.layer.testfolder
        new_rid = rid + u'-copied'
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        self.connector.copy(rid, new_rid)
        resource = self.connector[new_rid]
        self.assertEquals('Pop.', resource.data.read())

    def test_move(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/%s/ünicöde' % self.layer.testfolder
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
        rid = 'http://xml.zeit.de/%s/foo#bar' % self.layer.testfolder
        self.connector[rid] = zeit.connector.resource.Resource(
            rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        resource = self.connector[rid]
        self.assertEquals('Pop.', resource.data.read())


class ConflictDetectionBase(object):

    def setUp(self):
        from zeit.connector.interfaces import UUID_PROPERTY
        super(ConflictDetectionBase, self).setUp()
        rid = u'http://xml.zeit.de/%s/conflicting' % self.layer.testfolder
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
    ConflictDetectionBase, zeit.connector.testing.ConnectorTest):

    copy_inherited_functions(ConflictDetectionBase, locals())


class TestConflictDetectionMock(
    ConflictDetectionBase, zeit.connector.testing.MockTest):

    copy_inherited_functions(ConflictDetectionBase, locals())


class MoveConflictDetectionBase(object):

    def test_move_with_same_body_should_remove_original(self):
        source = self.get_resource('source', 'source-body')
        self.connector.add(source)
        target = self.get_resource('target', 'source-body')
        self.connector.add(target)
        self.connector.move(source.id, target.id)
        self.assertEqual(
            ['target'],
            [name for name, unique_id in
             self.connector.listCollection(
                 'http://xml.zeit.de/%s' % self.layer.testfolder) if name])

    def test_move_with_different_data_should_fail(self):
        source = self.get_resource('source', 'source-body')
        self.connector.add(source)
        target = self.get_resource('target', 'target-body')
        self.connector.add(target)
        with self.assertRaises(zeit.connector.interfaces.MoveError):
            self.connector.move(source.id, target.id)
        self.assertEqual(
            ['source', 'target'],
            [name for name, unique_id in
             self.connector.listCollection(
                 'http://xml.zeit.de/%s' % self.layer.testfolder) if name])

    def test_move_should_fail_if_target_is_existing_directory(self):
        source = self.get_resource('source', '',
                                   contentType='httpd/unix-directory')
        self.connector.add(source)
        target = self.get_resource('target', '',
                                   contentType='httpd/unix-directory')
        self.connector.add(target)
        with self.assertRaises(zeit.connector.interfaces.MoveError):
            self.connector.move(source.id, target.id)


class TestMoveConflictDetectionReal(
    MoveConflictDetectionBase, zeit.connector.testing.ConnectorTest):
    """Test move conflict with real connector and real DAV."""

    copy_inherited_functions(MoveConflictDetectionBase, locals())


class TestMoveConflictDetectionMock(
    MoveConflictDetectionBase, zeit.connector.testing.MockTest):
    """Test move conflict with mock connector."""

    copy_inherited_functions(MoveConflictDetectionBase, locals())


class TestResource(zeit.connector.testing.ConnectorTest):

    def test_properties_should_be_current(self):
        import zeit.connector.resource
        rid = u'http://xml.zeit.de/%s/aresource' % self.layer.testfolder
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

    def setUp(self):
        import zeit.connector.resource
        super(TestConnectorCache, self).setUp()
        self.rid = 'http://xml.zeit.de/%s/cache_test' % self.layer.testfolder
        self.connector[self.rid] = zeit.connector.resource.Resource(
            self.rid, None, 'text',
            StringIO.StringIO('Pop.'),
            contentType='text/plain')
        list(self.connector.listCollection(
            'http://xml.zeit.de/%s/' % self.layer.testfolder))

    def test_deleting_non_existing_resource_does_not_create_cache_entry(self):
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/%s/' % self.layer.testfolder]
        children.remove(self.rid)
        del self.connector[self.rid]
        self.assertEqual([], list(children))
        self.assertEqual(None, self.connector.property_cache.get(self.rid))

    def test_delete_updates_cache(self):
        del self.connector[self.rid]
        children = self.connector.child_name_cache[
            'http://xml.zeit.de/%s/' % self.layer.testfolder]
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
            [(u'cache_test',
              u'http://xml.zeit.de/%s/cache_test' % self.layer.testfolder)],
            list(self.connector.listCollection(
                'http://xml.zeit.de/%s/' % self.layer.testfolder)))
        cache = self.connector.child_name_cache[
            'http://xml.zeit.de/%s/' % self.layer.testfolder]
        self.assertEquals(
            [u'http://xml.zeit.de/%s/cache_test' % self.layer.testfolder],
            list(cache))
        cache.add('http://xml.zeit.de/%s/cache_test_2' % self.layer.testfolder)
        self.assertEquals(
            [(u'cache_test',
              u'http://xml.zeit.de/%s/cache_test' % self.layer.testfolder)],
            list(self.connector.listCollection(
                'http://xml.zeit.de/%s/' % self.layer.testfolder)))

    @unittest.expectedFailure
    def test_no_changes_should_not_cause_write(self):
        # Assign caches to DB to be able to detect changes.
        self.getRootFolder().property_cache = self.connector.property_cache
        self.getRootFolder().child_cache = self.connector.child_name_cache
        transaction.commit()

        jar = self.connector.property_cache._p_jar
        r = self.get_resource('res', 'Pop goes the weasel.')
        self.connector.add(r)
        list(self.connector.listCollection(
            'http://xml.zeit.de/%s/' % self.layer.testfolder))
        # Two changes: property cache and child chache
        self.assertTrue(jar._registered_objects)
        transaction.commit()
        # No changes.
        self.assertEqual([], jar._registered_objects)
        self.connector.invalidate_cache(r.id)
        self.assertEqual([], jar._registered_objects)

    def test_invalidation_on_folder_with_non_folder_id_should_not_fail(self):
        self.connector.invalidate_cache(
            'http://xml.zeit.de/%s' % self.layer.testfolder)

    def test_invalidation_with_redirect_should_clear_old_location_cache(self):
        del self.connector.property_cache[
            'http://xml.zeit.de/%s/' % self.layer.testfolder]
        self.connector.property_cache[
            'http://xml.zeit.de/%s' % self.layer.testfolder] = {
            ('foo', 'bar'): 'baz'}
        self.connector.child_name_cache[
            'http://xml.zeit.de/%s' % self.layer.testfolder] = [
            'a', 'b', 'c']
        self.connector.invalidate_cache(
            'http://xml.zeit.de/%s' % self.layer.testfolder)
        self.assertEqual(
            None,
            self.connector.property_cache.get(
                'http://xml.zeit.de/%s' % self.layer.testfolder))
        self.assertEqual(
            'httpd/unix-directory',
            self.connector.property_cache[
                'http://xml.zeit.de/%s/' % self.layer.testfolder][
                    ('getcontenttype', 'DAV:')])
        self.assertEqual(
            None,
            self.connector.child_name_cache.get(
                'http://xml.zeit.de/%s' % self.layer.testfolder))
        self.assertEqual(
            [self.rid],
            list(self.connector.child_name_cache.get(
                'http://xml.zeit.de/%s/' % self.layer.testfolder)))


class TestMove(zeit.connector.testing.ConnectorTest):

    def test_move_own_locked_resource_should_work(self):
        res = self.get_resource('foo', 'body')
        self.connector.add(res)
        self.connector.lock(res.id, 'userid', None)
        self.connector.move(
            res.id, 'http://xml.zeit.de/%s/bar' % self.layer.testfolder)
        self.connector['http://xml.zeit.de/%s/bar' % self.layer.testfolder]

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
                    res.id,
                    'http://xml.zeit.de/%s/bar' % self.layer.testfolder))
        finally:
            self.connector.unlock(res.id, token)

    def test_copy_locked_resource_should_work(self):
        res = self.get_resource('foo', 'body')
        self.connector.add(res)
        self.connector.lock(res.id, 'userid', None)
        self.connector.copy(
            res.id, 'http://xml.zeit.de/%s/bar' % self.layer.testfolder)
        self.connector['http://xml.zeit.de/%s/bar' % self.layer.testfolder]

    def test_move_collection_moves_all_members(self):
        coll = zeit.connector.resource.Resource(
            'http://xml.zeit.de/%s/foo' % self.layer.testfolder,
            'foo', 'collection', StringIO.StringIO(''))
        self.connector.add(coll)
        res = self.get_resource('foo/one', 'body')
        self.connector.add(res)
        res = self.get_resource('foo/two', 'body')
        self.connector.add(res)
        self.assertEqual(['one', 'two'], sorted([
            x[0] for x in self.connector.listCollection(
                'http://xml.zeit.de/%s/foo' % self.layer.testfolder)]))
        self.connector.move(
            coll.id, 'http://xml.zeit.de/%s/bar' % self.layer.testfolder)
        self.assertEqual(['one', 'two'], sorted([
            x[0] for x in self.connector.listCollection(
                'http://xml.zeit.de/%s/bar' % self.layer.testfolder)]))


class TestSearch(zeit.connector.testing.ConnectorTest):

    def test_should_raise_on_500(self):
        from zeit.connector.dav.interfaces import DAVError
        from zeit.connector.search import SearchVar
        var = SearchVar('name', 'namespace')
        result = self.connector.search([var], var == 'foo')
        with mock.patch('zeit.connector.dav.davresource.DAVResult') as dav:
            dav.has_errors.return_value = True
            self.assertRaises(
                DAVError, lambda: result.next())

    def test_should_convert_unicode(self):
        from zeit.connector.search import SearchVar
        var = SearchVar('name', 'namespace')
        result = self.connector.search([var], var == u'föö')
        try:
            # This call renders the search var, sends it to the server and
            # gets one result. If there is no result (which is likely)
            # StopIteration will be raised. This is okay as the test should
            # only assert that the unicode search var is correctly rendered
            # and sent to the server.
            result.next()
        except StopIteration:
            pass


class TestXMLSupport(zeit.connector.testing.ConnectorTest):

    def test_xml_strings_should_be_storable(self):
        res = self.get_resource('xmltest', '')
        res.properties[('foo', 'bar')] = '<a><b/></a>'
        self.connector.add(res)
        res = self.connector[res.id]
        self.assertEqual('<a><b/></a>', res.properties[('foo', 'bar')])

    def test_xml_properties_are_returned_with_surrounding_tag(self):
        import lxml.objectify
        res = self.get_resource('xmltest', '')
        res.properties[('foo', 'bar')] = (
            '<d:foo xmlns:d="bar"><a><b/></a></d:foo>')
        self.connector.add(res)
        res = self.connector[res.id]
        prop = lxml.objectify.fromstring(res.properties[('foo', 'bar')])
        self.assertEqual(
            ['a'], [n.tag for n in prop.getchildren()])


class TestTBCConnector(zeit.connector.testing.ConnectorTest):

    def setUp(self):
        connector = zeit.connector.connector.TransactionBoundCachingConnector(
            roots={'default': os.environ['connector-url'],
                   'search': os.environ['search-connector-url']})
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(connector, zeit.connector.interfaces.IConnector)

    def test_smoke(self):
        resource = self.connector[
            u'http://xml.zeit.de/online/2007/09/laktose-milchzucker-gewöhnung']
        resource.data
