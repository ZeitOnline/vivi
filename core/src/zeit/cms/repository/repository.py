from functools import total_ordering
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.interfaces import IRepositoryContent
import gocept.cache.property
import grokcore.component as grok
import logging
import os.path
import persistent
import re
import six
import zeit.cms.interfaces
import zeit.cms.redirect.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zeit.connector.dav.interfaces
import zeit.connector.interfaces
import zope.annotation.interfaces
import zope.app.appsetup.product
import zope.component
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.processlifetime
import zope.securitypolicy.interfaces


log = logging.getLogger('zeit.cms.repository')


@total_ordering
@zope.interface.implementer(zeit.cms.repository.interfaces.IDAVContent)
class ContentBase(zope.container.contained.Contained):
    """Base class for repository content."""

    uniqueId = None
    __name__ = None

    def __eq__(self, other):
        if not zeit.cms.interfaces.ICMSContent.providedBy(other):
            return False
        return self.uniqueId == other.uniqueId

    def __lt__(self, other):
        if not zeit.cms.interfaces.ICMSContent.providedBy(other):
            return False
        return self.uniqueId < other.uniqueId

    def __hash__(self):
        return hash(self.uniqueId)

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.uniqueId or '(unknown)')

    # Support the performance optimization in Repository.getContent()
    # by optionally resolving our parent ourselves.
    @property
    def __parent__(self):
        if hasattr(self, '__explicit_parent__'):
            return self.__explicit_parent__
        if not IRepositoryContent.providedBy(self):
            # This most likely means we're somewhere inside a workingcopy. The
            # default value in zope.container.Contained is None, and we also
            # need to handle bw-compat for ILocalContent objects that existed
            # before __explicit_parent__ was introduced.
            return self.__dict__.get('__parent__')

        unique_id = self.uniqueId
        trailing_slash = unique_id.endswith('/')
        if trailing_slash:
            unique_id = unique_id[:-1]
        parent_id = os.path.dirname(unique_id)
        parent_id = parent_id.rstrip('/') + '/'

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        # "root" edge case part 1a: We use the repository itself as the '/'
        # folder, it serves as the traversal root for DAV content
        if parent_id == repository.uniqueId:
            return repository
        return repository.getContent(parent_id)

    @__parent__.setter
    def __parent__(self, value):
        self.__explicit_parent__ = value

    @__parent__.deleter
    def __parent__(self):
        if hasattr(self, '__explicit_parent__'):
            del self.__explicit_parent__


@zope.interface.implementer(zeit.cms.repository.interfaces.ICollection)
class Container(ContentBase):
    """The container represents webdav collections."""

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
        content = self.repository._getContent(unique_id)
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
            try:
                yield self[key]
            except KeyError:
                # The connector childname cache has been seen to contain
                # entries that don't actually exist in DAV (anymore?), #5993.
                continue

    def __len__(self):
        '''See interface `IReadContainer`'''
        return len(self._local_unique_map)

    def items(self):
        '''See interface `IReadContainer`'''
        return list(zip(list(self.keys()), list(self.values())))

    def __contains__(self, key):
        '''See interface `IReadContainer`'''
        return key in self._local_unique_map

    has_key = __contains__

    def __setitem__(self, name, object):
        '''See interface `IWriteContainer`'''
        # We need to store oldparent before changing object.uniqueId, since
        # ContentBase otherwise may start calculating a wrong value.
        oldparent = object.__parent__
        oldname = object.__name__

        new_id = self._get_id_for_name(name)
        if object.uniqueId is None:
            # This is a new object as it didn't have a uniqueId, yet.
            object.uniqueId = new_id
            event = True
        else:
            # This is an existing object which is updated, copied or moved.
            event = False

        if new_id == object.uniqueId:
            # Object only needs updating.
            self.repository.addContent(object)
        elif oldparent:
            # As the object has a parent we assume that it should be moved.
            log.info("Moving %s to %s" % (object.uniqueId, new_id))
            self.connector.move(object.uniqueId, new_id)
            object.uniqueId = new_id
            event = True
        else:
            # As the object has no parent we assume that it should be copied.
            log.info("Copying %s to %s" % (object.uniqueId, new_id))
            self.connector.copy(object.uniqueId, new_id)
            event = True

        self._local_unique_map_data.clear()
        if event:
            # Just the salient part of zope.container.contained.containedEvent,
            # since we have to handle oldparent ourselves.
            object.__parent__ = self
            object.__name__ = name
            if oldparent is None or oldname is None:
                event = zope.lifecycleevent.ObjectAddedEvent(
                    object, self, name)
            else:
                event = zope.lifecycleevent.ObjectMovedEvent(
                    object, oldparent, oldname, self, name)
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


@zope.interface.implementer(
    zeit.cms.repository.interfaces.IRepository,
    zeit.cms.repository.interfaces.IFolder,
    zeit.cms.repository.interfaces.IRepositoryContent,
    zeit.cms.section.interfaces.IZONSection,
    zope.annotation.interfaces.IAttributeAnnotatable)
class Repository(persistent.Persistent, Container):
    """Access the webdav repository."""

    # "root" edge case part 2, allow the ZODB folder to set itself as the
    # parent when installing the Repository object, since the DAV hierarchy
    # ends there and changes over to the ZODB hierarchy.
    __parent__ = None
    uniqueId = zeit.cms.interfaces.ID_NAMESPACE

    _content = gocept.cache.property.TransactionBoundCache('_v_content', dict)

    def __init__(self):
        self._initalizied = False

    def keys(self):
        if not self._initalizied:
            return []
        return super().keys()

    def getContent(self, unique_id):
        if not isinstance(unique_id, six.string_types):
            raise TypeError("unique_id: string expected, got %s" %
                            type(unique_id))
        unique_id = self._get_normalized_unique_id(unique_id)
        if not unique_id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
            raise ValueError("The id %r is invalid." % unique_id)
        if unique_id == self.uniqueId:  # "root" edge case part 1b
            return self

        try:
            # Performance optimization: Most content can be resolved directly
            # via the connector, which is much faster than using traversal.
            # To support this, content objects (via ContentBase above) are
            # location-aware and can resolve their __parent__ themselves
            # if it is needed (instead of the usual Zope paradigm that the
            # container writes it on its children from the outside).
            content = self._getContent(unique_id)
        except KeyError:
            # Some content cannot be resolved directly, the most prominent
            # example being zeit.content.dynamicfolder.
            path = unique_id.replace(zeit.cms.interfaces.ID_NAMESPACE, '', 1)
            if path.startswith('/'):
                path = path[1:]
            try:
                content = zope.traversing.interfaces.ITraverser(
                    self).traverse(path)
            except zope.traversing.interfaces.TraversalError:
                raise KeyError(unique_id)
        return content

    def _getContent(self, unique_id):
        try:
            content = self._content[unique_id]
        except KeyError:
            content = self.getCopyOf(unique_id)
            self._add_marker_interfaces(content)
            self._content[unique_id] = content
        return content

    def _add_marker_interfaces(self, content):  # Extension point for zeit.web
        zope.interface.alsoProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)

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

    def getCopyOf(self, unique_id):
        log.debug('Getting resource %s' % unique_id)
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


@zope.component.adapter(zope.processlifetime.IDatabaseOpenedWithRoot)
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
def invalidate_content_cache(event):
    repository = zope.component.queryUtility(
        zeit.cms.repository.interfaces.IRepository)
    if repository is not None:
        repository._content.pop(event.id, None)


@grok.adapter(six.string_types[0], name=zeit.cms.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_content(uniqueId):
    repository = zope.component.queryUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        return repository.getContent(uniqueId)
    except (ValueError, KeyError):
        lookup = zope.component.getUtility(
            zeit.cms.redirect.interfaces.ILookup)
        new_id = lookup.find(uniqueId)
        if new_id:
            return zeit.cms.interfaces.ICMSContent(new_id, None)
        else:
            return None


@grok.adapter(six.string_types[0], name=zeit.cms.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSWCContent)
def unique_id_to_wc_or_repository(uniqueId):
    wc = zope.component.queryAdapter(
        None, zeit.cms.workingcopy.interfaces.IWorkingcopy)
    wc_values = wc.values() if wc is not None else []
    obj = None
    for obj in wc_values:
        if not zeit.cms.interfaces.ICMSContent.providedBy(obj):
            continue
        if obj.uniqueId == uniqueId:
            break
    else:
        obj = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    return obj


# XXX kludgy heuristics, these URLs are defined in XSLT somewhere
IGNORED_LIVE_PAGE_SUFFIXES = re.compile(r'/((seite-\d+)|(komplettansicht))/?$')
IGNORED_VIVI_SUFFIXES = re.compile(r'/@@.*$')


@grok.adapter(six.string_types[0], name='http://www.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def live_url_to_content(uniqueId):
    uniqueId = uniqueId.replace('www', 'xml', 1)
    uniqueId = IGNORED_LIVE_PAGE_SUFFIXES.sub('', uniqueId)
    return zeit.cms.interfaces.ICMSContent(uniqueId, None)


@grok.adapter(six.string_types[0], name='https://www.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def live_https_url_to_content(uniqueId):
    uniqueId = uniqueId.replace('https://www', 'http://xml', 1)
    uniqueId = IGNORED_LIVE_PAGE_SUFFIXES.sub('', uniqueId)
    return zeit.cms.interfaces.ICMSContent(uniqueId, None)


@grok.adapter(six.string_types[0], name='http://vivi.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def vivi_url_to_content(uniqueId):
    prefix = 'http://vivi.zeit.de/repository/'
    if not uniqueId.startswith(prefix):
        return None
    uniqueId = uniqueId.replace(prefix, zeit.cms.interfaces.ID_NAMESPACE, 1)
    uniqueId = IGNORED_VIVI_SUFFIXES.sub('', uniqueId)
    return zeit.cms.interfaces.ICMSContent(uniqueId, None)


@grok.adapter(six.string_types[0], name='https://vivi.zeit.de/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def vivi_https_url_to_content(uniqueId):
    prefix = 'https://vivi.zeit.de/repository/'
    if not uniqueId.startswith(prefix):
        return None
    uniqueId = uniqueId.replace(prefix, zeit.cms.interfaces.ID_NAMESPACE, 1)
    uniqueId = IGNORED_VIVI_SUFFIXES.sub('', uniqueId)
    return zeit.cms.interfaces.ICMSContent(uniqueId, None)


@grok.adapter(six.string_types[0], name='<no-scheme>://<no-netloc>/')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def no_scheme_unique_id_to_cms_content(unique_id):
    # try repository
    return unique_id_to_content(unique_id)
