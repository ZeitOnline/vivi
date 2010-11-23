# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.cache.property
import zope.lifecycleevent
import grokcore.component
import logging
import persistent
import transaction
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.connector.dav.interfaces
import zeit.connector.interfaces
import zope.annotation.interfaces
import zope.app.appsetup.product
import zope.container.contained
import zope.container.interfaces
import zope.cachedescriptors.method
import zope.component
import zope.component.interfaces
import zope.interface
import zope.securitypolicy.interfaces


log = logging.getLogger('zeit.cms.repository')


class Container(zope.container.contained.Contained):
    """The container represents webdav collections."""

    zope.interface.implements(zeit.cms.repository.interfaces.ICollection)

    uniqueId = None
    _local_unique_map_data = gocept.cache.property.TransactionBoundCache(
            '_v_local_unique_map', dict)

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
        zope.interface.alsoProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)
        return zope.container.contained.contained(
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
            # This is a new object as it didn't have a uniqueId, yet.
            object.uniqueId = new_id
            event = True
        else:
            # This is an existing object which is updated, copied or moved.
            event = False

        if new_id == object.uniqueId:
            # Object only needs opdating.
            self.repository.addContent(object)
        elif object.__parent__:
            # As the object has a parent we assume that it should be moved.
            log.info("Moving %s to %s" % (object.uniqueId, new_id))
            self.connector.move(object.uniqueId, new_id)
            event = True
        else:
            # As the object has a no parent we assume that it should be copied.
            log.info("Copying %s to %s" % (object.uniqueId, new_id))
            self.connector.copy(object.uniqueId, new_id)
            event = True

        self._local_unique_map_data.clear()
        if event:
            object, event = zope.container.contained.containedEvent(
                object, self, name)
            zope.event.notify(event)

    def __delitem__(self, name):
        '''See interface `IWriteContainer`'''

        obj = self[name]

        zope.event.notify(
            zeit.cms.repository.interfaces.BeforeObjectRemovedEvent(obj))

        id = self._get_id_for_name(name)
        del self.connector[id]
        self._local_unique_map_data.clear()

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
            separator = ''
        else:
            separator = '/'
        return separator.join((self.uniqueId, name))

    @property
    def _local_unique_map(self):
        __traceback_info__ = (self.uniqueId,)
        if not self._local_unique_map_data:
            self._local_unique_map_data.update(
                self.connector.listCollection(self.uniqueId))
        return self._local_unique_map_data


class Repository(persistent.Persistent, Container):
    """Access the webdav repository."""

    zope.interface.implements(
        zeit.cms.repository.interfaces.IRepository,
        zeit.cms.repository.interfaces.IFolder,
        zeit.cms.repository.interfaces.IRepositoryContent,
        zope.annotation.interfaces.IAttributeAnnotatable)

    uniqueId = zeit.cms.interfaces.ID_NAMESPACE
    uncontained_content = gocept.cache.property.TransactionBoundCache(
        '_v_uncontained_content', dict)

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
        unique_id = self._get_normalized_unique_id(unique_id)
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

    def getUncontainedContent(self, unique_id):
        try:
            content = self.uncontained_content[unique_id]
        except KeyError:
            content = self._get_uncontained_copy(unique_id)
            self.uncontained_content[unique_id] = content
        return content

    def addContent(self, content, ignore_conflicts=False):
        zope.event.notify(
            zeit.cms.repository.interfaces.BeforeObjectAddEvent(content))
        resource = zeit.cms.interfaces.IResource(content)
        if resource.id is None:
            raise ValueError("Objects to be added to the repository need a "
                             "unique id.")
        try:
            self.connector.add(resource, verify_etag=not ignore_conflicts)
        except zeit.connector.dav.interfaces.PreconditionFailedError:
            raise zeit.cms.repository.interfaces.ConflictError(
                content.uniqueId,
                _('There was a conflict while adding ${name}',
                  mapping=dict(name=content.uniqueId)))

    @property
    def repository(self):
        return self

    def _get_uncontained_copy(self, unique_id):
        log.debug("Getting resource %r" % unique_id)
        resource = self.connector[unique_id]
        content = zeit.cms.interfaces.ICMSContent(resource)
        content.__name__ = resource.__name__
        return content

    def _get_normalized_unique_id(self, unique_id):
        if unique_id.startswith('/cms/work/'):
            return unique_id.replace('/cms/work/',
                                     zeit.cms.interfaces.ID_NAMESPACE)
        return unique_id


def repositoryFactory():
    repository = Repository()
    deny_edit_permissions_in_repository(repository)
    return repository


@zope.component.adapter(zeit.cms.repository.interfaces.IRepository,
                        zope.lifecycleevent.IObjectAddedEvent)
def initializeRepository(repository, event):
    repository._initalizied = True


@zope.component.adapter(
    zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
def deny_edit_permissions_in_repository_on_startup(event):
    root = event.database.open().root()
    root_folder = root[
        zope.app.publication.zopepublication.ZopePublication.root_name]
    repository = root_folder['repository']
    deny_edit_permissions_in_repository(repository)


def deny_edit_permissions_in_repository(repository):
    perms = zope.securitypolicy.interfaces.IPrincipalPermissionManager(
        repository)
    for perm_id, perm in zope.component.getUtilitiesFor(
        zeit.cms.interfaces.IEditPermission):
        perms.denyPermissionToPrincipal(perm_id, 'zope.Everybody')


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def cmscontentFactory(context):
    """Master adapter for adapting Resources to CMSContent.

    It creates the CMSContent by finding an adapter which is registered with
    the name of the resource type.

    """
    def adapter(type):
        return zope.component.queryAdapter(
            context, zeit.cms.interfaces.ICMSContent, type)

    content = adapter(context.type)
    if content is None:
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        default_type = None
        if cms_config:
            default_type = cms_config.get('default-type')
        if default_type is None:
            default_type = 'unknown'
        content = adapter(default_type)

    if content is not None:
        content.uniqueId = context.id

    zope.event.notify(
        zeit.cms.repository.interfaces.AfterObjectConstructedEvent(content,
                                                                   context))
    return content


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_uncontained_content(event):
    repository = zope.component.queryUtility(
        zeit.cms.repository.interfaces.IRepository)
    if repository is not None:
        repository.uncontained_content.pop(event.id, None)


@grokcore.component.adapter(basestring,
                            name=zeit.cms.interfaces.ID_NAMESPACE)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_content(uniqueId):
    repository = zope.component.queryUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        return repository.getContent(uniqueId)
    except (ValueError, KeyError):
        return None


@grokcore.component.adapter(basestring, name='<no-scheme>://<no-netloc>/')
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def no_scheme_unique_id_to_cms_content(unique_id):
    # try repository
    return unique_id_to_content(unique_id)
