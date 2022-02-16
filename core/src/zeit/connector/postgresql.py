from functools import partial
from gocept.cache.property import TransactionBoundCache
from google.cloud import storage
from io import BytesIO
from logging import getLogger
from sqlalchemy import Boolean, TIMESTAMP, Unicode
from sqlalchemy import Column, ForeignKey, select, delete
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from uuid import uuid4
from zeit.connector.dav.interfaces import DAVNotFoundError
from zeit.connector.resource import CachedResource
import collections
import os
import os.path
import sqlalchemy
import sqlalchemy.orm
import transaction
import zeit.connector.interfaces
import zope.interface
import zope.sqlalchemy


log = getLogger(__name__)


ID_NAMESPACE = zeit.connector.interfaces.ID_NAMESPACE[:-1]


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
class Connector:

    def __init__(self, dsn, storage_project, storage_bucket):
        self.dsn = dsn
        self.engine = sqlalchemy.create_engine(dsn, future=True)
        self.session = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine, future=True))
        zope.sqlalchemy.register(self.session)
        self.gcs_client = storage.Client(project=storage_project)
        self.bucket = self.gcs_client.bucket(storage_bucket)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.connector') or {}
        return cls(
            config['dsn'], config['storage-project'], config['storage-bucket'])

    def __getitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        props = self._get_properties(uniqueid)
        if props is None:
            raise KeyError(uniqueid)
        if props.is_collection:
            _get_body = partial(BytesIO, b'')
        else:
            _get_body = partial(self._get_body, props.id)
        return CachedResource(
            uniqueid, uniqueid.split('/')[-1], props.type,
            props.to_webdav, _get_body,
            'httpd/unix-directory' if props.is_collection else 'httpd/unknown')

    property_cache = TransactionBoundCache('_v_property_cache', dict)

    def _get_properties(self, uniqueid):
        props = self.property_cache.get(uniqueid)
        if props is not None:
            return props
        path = self.session.get(Paths, self._pathkey(uniqueid))
        if path is not None:
            props = path.properties
            self.property_cache[uniqueid] = props
        return props

    body_cache = TransactionBoundCache('_v_body_cache', dict)

    def _get_body(self, id):
        body = self.body_cache.get(id)
        if body is not None:
            return BytesIO(body)
        blob = self.bucket.blob(id)
        body = blob.download_as_bytes()
        self.body_cache[id] = body
        return BytesIO(body)

    def __contains__(self, uniqueid):
        try:
            self[uniqueid]
            return True
        except KeyError:
            return False

    def listCollection(self, uniqueid):
        if uniqueid not in self:
            # XXX mimic DAV behaviour (which likely should be KeyError instead)
            raise DAVNotFoundError(404, 'Not Found', uniqueid, '')
        uniqueid = self._normalize(uniqueid)
        parent_path = '/'.join(self._pathkey(uniqueid))
        for name in self.session.execute(
                select(Paths.name)
                .filter_by(parent_path=parent_path)).scalars():
            yield (name, f"{ID_NAMESPACE}{parent_path}/{name}")

    def __setitem__(self, uniqueid, resource):
        resource.id = uniqueid
        self.add(resource)

    def add(self, resource, verify_etag=True):
        uniqueid = self._normalize(resource.id)
        props = self._get_properties(uniqueid)
        exists = props is not None
        if not exists:
            props = Properties()
            path = Paths(properties=props)
            self.session.add(path)
        else:
            path = props.path

        (path.parent_path, path.name) = self._pathkey(uniqueid)
        props.from_webdav(resource.properties)
        props.type = resource.type
        props.is_collection = resource.contentType == 'httpd/unix-directory'

        if not props.is_collection:
            self.body_cache.pop(props.id, None)
            blob = self.bucket.blob(props.id)
            resource.data.seek(0)
            blob.upload_from_file(resource.data)

        if uniqueid in self.property_cache:
            self.property_cache[uniqueid] = props
            resource.data.seek(0)
            self.body_cache[uniqueid] = resource.data.read()

    def changeProperties(self, uniqueid, properties):
        uniqueid = self._normalize(uniqueid)
        props = self._get_properties(uniqueid)
        if props is None:
            raise KeyError(uniqueid)
        current = props.to_webdav()
        current.update(properties)
        props.from_webdav(current)
        if uniqueid in self.property_cache:
            self.property_cache[uniqueid] = props

    def __delitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        (parent_path, name) = self._pathkey(uniqueid)
        self.session.execute(
            delete(Paths)
            .filter_by(parent_path=parent_path, name=name))
        self.property_cache.pop(uniqueid, None)
        self.body_cache.pop(uniqueid, None)

    @staticmethod
    def _normalize(uniqueid):
        if not uniqueid.startswith(ID_NAMESPACE):
            raise ValueError('The id %r is invalid.' % uniqueid)
        return uniqueid.rstrip('/')

    @staticmethod
    def _pathkey(uniqueid):
        (parent_path, name) = os.path.split(
            uniqueid.replace(ID_NAMESPACE, '', 1))
        parent_path = parent_path.rstrip('/')
        return (parent_path, name)

    def copy(self, old_uniqueid, new_uniqueid):
        pass

    def move(self, old_uniqueid, new_uniqueid):
        pass

    def lock(self, uniqueid, principal, until):
        pass

    def unlock(self, uniqueid, locktoken=None):
        pass

    def locked(self, uniqueid):
        pass

    def search(self, attributes, expression):
        pass


factory = Connector.factory


METADATA = sqlalchemy.MetaData()
DBObject = sqlalchemy.orm.declarative_base(metadata=METADATA)


class Paths(DBObject):

    __tablename__ = 'paths'
    __table_args__ = (
        UniqueConstraint('parent_path', 'name', 'id'),
    )

    parent_path = Column(Unicode, primary_key=True, index=True)
    name = Column(Unicode, primary_key=True)

    id = Column(UUID, ForeignKey('properties.id', ondelete='cascade'))
    properties = relationship(
        'Properties', uselist=False, lazy='joined',
        backref=backref('path', uselist=False))


class Properties(DBObject):

    __tablename__ = 'properties'

    id = Column(UUID, primary_key=True)
    type = Column(Unicode, nullable=False, server_default='unknown')
    is_collection = Column(Boolean, nullable=False, server_default='false')

    unsorted = Column(JSONB)

    last_updated = Column(
        TIMESTAMP(timezone=True),
        server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())

    NS = 'http://namespaces.zeit.de/CMS/'

    def to_webdav(self):
        props = {}
        for ns, d in self.unsorted.items():
            for k, v in d.items():
                props[(k, self.NS + ns)] = v

        props[('uuid', self.NS + 'document')] = '{urn:uuid:%s}' % self.id
        props[('type', self.NS + 'meta')] = self.type

        return props

    def from_webdav(self, props):
        if not self.id:
            assert not self.path.id
            id = props.get(('uuid', self.NS + 'document'))
            if id is None:
                id = str(uuid4())
            else:
                id = id[10:-1]  # strip off `{urn:uuid:}`
            self.id = id
            self.path.id = id

        unsorted = collections.defaultdict(dict)
        for (k, ns), v in props.items():
            unsorted[ns.replace(self.NS, '', 1)][k] = v
        self.unsorted = unsorted


class PassthroughConnector(Connector):
    """Development helper that transparently imports content objects (whenever
    they are accessed) into SQL from another ("upstream") Connector.
    This offers a quick way to getting started, without having to perform any
    elaborate migration steps first, but it is meant for convenience only,
    not any kind of production use.
    """

    def __init__(self, dsn, storage_project, storage_bucket, repository_path):
        import zeit.connector.filesystem
        import zeit.connector.zopeconnector

        super().__init__(dsn, storage_project, storage_bucket)
        METADATA.create_all(self.engine)  # convenience
        if repository_path.startswith('http'):
            self.upstream = zeit.connector.zopeconnector.ZopeConnector(
                {'default': repository_path})
        else:
            self.upstream = zeit.connector.filesystem.Connector(
                repository_path)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.connector') or {}
        return cls(
            config['dsn'],
            config['storage-project'], config['storage-bucket'],
            config['repository-path'])

    def __getitem__(self, id):
        try:
            return super().__getitem__(id)
        except KeyError:
            return self._import(id)

    def _import(self, id):
        log.debug("_import %s", id)
        resource = self.upstream[id]
        # Hacky. Remove this as it is not json-serializable, and also
        # irrelevant except for DAV caches.
        resource.properties.data.pop(('cached-time', 'INTERNAL'), None)
        savepoint = self.session.begin_nested()
        self[id] = resource
        try:
            self.session.flush()
        except sqlalchemy.exc.IntegrityError as e:
            log.critical("Can't import %s: %s", id, e)
            savepoint.rollback()
            raise KeyError(id)
        else:
            savepoint.commit()
            transaction.commit()
        return resource

    def listCollection(self, id):
        if id not in self:
            self._import(id)
        return super().listCollection(id)


passthrough_factory = PassthroughConnector.factory
