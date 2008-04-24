# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging

import persistent
import transaction

import zope.annotation.interfaces
import zope.cachedescriptors.method
import zope.interface
import zope.securitypolicy.interfaces

import zope.app.container.contained

import zeit.connector.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces


logger = logging.getLogger('zeit.cms.repository')


class Container(zope.app.container.contained.Contained):
    """The container represents webdav collections."""

    zope.interface.implements(zeit.cms.repository.interfaces.ICollection)

    uniqueId = None

    # Container interface

    def keys(self):
        """The keys are the filenames."""
        return sorted(self._local_unique_map.keys())

    def __iter__(self):
        '''See interface `IReadContainer`'''
        return iter(self.keys())

    def __getitem__(self, key):
        '''See interface `IReadContainer`'''
        unique_id = self._get_id_for_name(key)
        __traceback_info__ = (key, unique_id)
        content = self.repository.getUncontainedContent(unique_id)
        zope.interface.directlyProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)
        return zope.app.container.contained.contained(
            content, self, content.__name__)

    def get(self, key, default=None):
        '''See interface `IReadContainer`'''
        try:
            return self[key]
        except KeyError:
            return default

    def values(self):
        '''See interface `IReadContainer`'''
        for key in self.keys():
            yield self[key]

    def __len__(self):
        '''See interface `IReadContainer`'''
        return len(self._local_unique_map)

    def items(self):
        '''See interface `IReadContainer`'''
        return zip(self.keys(), self.values())

    def __contains__(self, key):
        '''See interface `IReadContainer`'''
        return key in self._local_unique_map

    has_key = __contains__

    def __setitem__(self, name, object):
        '''See interface `IWriteContainer`'''
        new_id = self._get_id_for_name(name)
        if object.uniqueId is None:
            object.uniqueId = new_id

        if new_id == object.uniqueId:
            # Update resource.
            self.repository.addContent(object)
        else:
            logger.info("Copying %s to %s" % (object.uniqueId, new_id))
            self.connector.copy(object.uniqueId, new_id)

        object, event = zope.app.container.contained.containedEvent(
            object, self, name)
        self._invalidate_cache()
        zope.event.notify(event)

    def __delitem__(self, name):
        '''See interface `IWriteContainer`'''
        id = self._get_id_for_name(name)
        del self.connector[id]
        self._invalidate_cache()

    # Internal helper methods and properties:

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def _get_id_for_name(self, name):
        if self.uniqueId.endswith('/'):
            slash = ''
        else:
            slash = '/'
        return '%s%s%s' % (self.uniqueId, slash, name)

    @zope.cachedescriptors.property.cachedIn('_v_local_unique_map')
    def _local_unique_map(self):
        transaction.get().addBeforeCommitHook(self._invalidate_cache)
        return dict(self.connector.listCollection(self.uniqueId))

    def _invalidate_cache(self):
        logger.debug('Invalidating %s' % self.uniqueId)
        try:
            delattr(self, '_v_local_unique_map')
        except AttributeError:
            pass
        self.repository._invalidate_content_cache()


class Repository(persistent.Persistent, Container):
    """Access the webdav repository."""

    zope.interface.implements(zeit.cms.repository.interfaces.IRepository,
                              zeit.cms.repository.interfaces.IFolder,
                              zope.annotation.interfaces.IAttributeAnnotatable)

    uniqueId = zeit.cms.interfaces.ID_NAMESPACE
    _v_registered = False

    def __init__(self):
        self._initalizied = False

    def keys(self):
        if not self._initalizied:
            return []
        keys = super(Repository, self).keys()
        try:
            keys.remove(u'online')
        except KeyError:
            pass
        else:
            keys.insert(0, u'online')
        return keys

    def getContent(self, unique_id):
        if not isinstance(unique_id, basestring):
            raise TypeError("unique_id: string expected, got %s" %
                            type(unique_id))
        if not unique_id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
            raise ValueError("The id %r is invalid." % unique_id)
        path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '', 1)
        if path.startswith('/'):
            path = path[1:]
        try:
            content = zope.traversing.interfaces.ITraverser(
                self).traverse(path)
        except zope.traversing.interfaces.TraversalError:
            raise KeyError(unique_id)
        return content

    def getCopyOf(self, unique_id):
        contained_content = self.getContent(unique_id)
        content = self._get_uncontained_copy(unique_id)
        content.__parent__ = contained_content.__parent__
        return content

    @zope.cachedescriptors.method.cachedIn('_v_uncontained_content')
    def getUncontainedContent(self, unique_id):
        if not self._v_registered:
            self._v_register = True
            transaction.get().addBeforeCommitHook(
                self._invalidate_content_cache)
        content = self._get_uncontained_copy(unique_id)
        return content

    def addContent(self, content):
        resource = zeit.cms.interfaces.IResource(content)
        if resource.id is None:
            raise ValueError("Objects to be added to the repository need a "
                             "unique id.")
        self.getUncontainedContent.invalidate(self, resource.id)
        self.connector.add(resource)

    @property
    def repository(self):
        return self

    def _get_uncontained_copy(self, unique_id):
        logger.debug("Getting resource %r" % unique_id)
        resource = self.connector[unique_id]
        content = zeit.cms.interfaces.ICMSContent(resource)
        content.__name__ = resource.__name__
        return content

    def _invalidate_content_cache(self):
        try:
            del self._v_uncontained_content
        except AttributeError:
            pass


def repositoryFactory():
    repository = Repository()
    # Deny EditContent to everybody (i.e. also to managers) because this really
    # really must not be possible.
    perms = zope.securitypolicy.interfaces.IPrincipalPermissionManager(
        repository)
    perms.denyPermissionToPrincipal('zeit.EditContent', 'zope.Everybody')

    # Grant zope.ManageContent to zeit.Editor so editors can lock/unlock
    # content.
    rpm = zope.securitypolicy.interfaces.IRolePermissionManager(
        repository)
    rpm.grantPermissionToRole('zope.ManageContent', 'zeit.Editor')
    return repository


@zope.component.adapter(zeit.cms.repository.interfaces.IRepository,
                        zope.app.container.interfaces.IObjectAddedEvent)
def initializeRepository(repository, event):
    repository._initalizied = True


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def cmscontentFactory(context):
    """Master adapter for adapting Resources to CMSContent.

    It creates the CMSContent by finding an adapter which is registered with
    the name of the resource type.

    """
    def adapter(type):
        return zope.component.getAdapter(
            context, zeit.cms.interfaces.ICMSContent, type)
    try:
        content = adapter(context.type)
    except zope.component.interfaces.ComponentLookupError:
        content = adapter('unknown')

    content.uniqueId = context.id
    return content
