from enum import Enum
from functools import partial
from io import BytesIO, StringIO
from logging import getLogger
from operator import itemgetter
from uuid import uuid4
import collections
import hashlib
import os
import os.path
import time

from gocept.cache.property import TransactionBoundCache
from google.cloud import storage
from google.cloud.storage.retry import DEFAULT_RETRY
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    ForeignKey,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Uuid,
    delete,
    insert,
    schema,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship
import google.api_core.exceptions
import opentelemetry.instrumentation.sqlalchemy
import opentelemetry.metrics
import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm
import transaction
import zope.component
import zope.interface
import zope.sqlalchemy

from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.connector.interfaces import (
    CopyError,
    DeleteProperty,
    LockedByOtherSystemError,
    LockingError,
    MoveError,
)
from zeit.connector.resource import CachedResource, Resource
import zeit.cms.interfaces
import zeit.cms.tracing
import zeit.connector.interfaces


log = getLogger(__name__)


ID_NAMESPACE = zeit.connector.interfaces.ID_NAMESPACE[:-1]


class LockStatus(Enum):
    NO_LOCK = 0
    OTHERS_LOCK = 1
    OWN_LOCK = 2


def _build_filter(expr):
    op = expr.operator
    if op == 'and':
        return sqlalchemy.and_(*(_build_filter(e) for e in expr.operands))
    elif op == 'eq':
        (var, value) = expr.operands
        name = var.name
        namespace = var.namespace.replace(Content.NS, '', 1)
        return Content.unsorted[namespace][name].as_string() == value
    else:
        raise RuntimeError(f'Unknown operand {op!r} while building search query')


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
class Connector:
    def __init__(self, dsn, storage_project, storage_bucket, reconnect_tries=3, reconnect_wait=0.1):
        self.dsn = dsn
        self.reconnect_tries = reconnect_tries
        self.reconnect_wait = reconnect_wait
        self.engine = sqlalchemy.create_engine(dsn, future=True)
        sqlalchemy.event.listen(self.engine, 'engine_connect', self._reconnect)
        self.session = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine, future=True)
        )
        zope.sqlalchemy.register(self.session)
        EngineTracer(self.engine, enable_commenter=True)
        self.gcs_client = storage.Client(project=storage_project)
        self.bucket = self.gcs_client.bucket(storage_bucket)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product

        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        params = {}
        reconnect_tries = config.get('sql-reconnect-tries')
        if reconnect_tries is not None:
            params['reconnect_tries'] = int(reconnect_tries)
        reconnect_wait = config.get('sql-reconnect-wait')
        if reconnect_wait is not None:
            params['reconnect_wait'] = float(reconnect_wait)
        return cls(config['dsn'], config['storage-project'], config['storage-bucket'], **params)

    # Inspired by <https://docs.sqlalchemy.org/en/20/core/pooling.html
    #   #custom-legacy-pessimistic-ping>
    def _reconnect(self, connection):
        attempt = 0
        while True:
            attempt += 1
            t = None
            try:
                t = connection.begin()
                connection.scalar(select(1))
                t.rollback()
            except Exception:
                if t:
                    t.rollback()
                if attempt >= self.reconnect_tries:
                    raise
                wait = self.reconnect_wait * attempt
                log.warning('Reconnecting in %s due to error', wait, exc_info=True)
                time.sleep(wait)
            else:
                break

    def __getitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        if content.is_collection:
            _get_body = partial(BytesIO, b'')
        elif content.binary_body:
            _get_body = partial(self._get_body, content.id)
        elif not content.body:
            _get_body = partial(BytesIO, b'')
        else:
            _get_body = partial(BytesIO, content.body.encode('utf-8'))
        return CachedResource(
            uniqueid,
            uniqueid.split('/')[-1],
            content.type,
            content.to_webdav,
            _get_body,
            'httpd/unix-directory' if content.is_collection else 'httpd/unknown',
        )

    property_cache = TransactionBoundCache('_v_property_cache', dict)

    def _get_content(self, uniqueid):
        content = self.property_cache.get(uniqueid)
        if content is not None:
            return content
        path = self.session.get(Path, self._pathkey(uniqueid))
        if path is not None:
            content = path.content
            self.property_cache[uniqueid] = content
        return content

    body_cache = TransactionBoundCache('_v_body_cache', dict)

    def _get_body(self, id):
        body = self.body_cache.get(id)
        if body is not None:
            return BytesIO(body)
        blob = self.bucket.blob(id)
        with zeit.cms.tracing.use_span(
            __name__ + '.tracing', 'gcs', attributes={'db.operation': 'download', 'id': id}
        ):
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
            raise KeyError(f'The resource {uniqueid} does not exist.')
        uniqueid = self._normalize(uniqueid)
        parent_path = '/'.join(self._pathkey(uniqueid))
        for name in self.session.execute(
            select(Path.name).filter_by(parent_path=parent_path)
        ).scalars():
            yield (name, f'{ID_NAMESPACE}{parent_path}/{name}')

    def __setitem__(self, uniqueid, resource):
        resource.id = uniqueid
        self.add(resource)

    def add(self, resource, verify_etag=True):
        uniqueid = self._normalize(resource.id)
        if uniqueid == ID_NAMESPACE:
            raise KeyError(f'Cannot write {uniqueid} to root object')
        content = self._get_content(uniqueid)
        exists = content is not None
        if not exists:
            content = Content()
            path = Path(content=content)
            self.session.add(path)
        else:
            path = content.path

        (path.parent_path, path.name) = self._pathkey(uniqueid)
        content.from_webdav(resource.properties)
        content.type = resource.type
        content.is_collection = resource.contentType == 'httpd/unix-directory'

        if not content.is_collection:
            self.body_cache.pop(content.id, None)
            if content.binary_body:
                blob = self.bucket.blob(content.id)
                data = resource.data  # may not be a static property
                size = data.seek(0, os.SEEK_END)
                data.seek(0)
                with zeit.cms.tracing.use_span(
                    __name__ + '.tracing',
                    'gcs',
                    attributes={'db.operation': 'upload', 'id': content.id, 'size': str(size)},
                ):
                    blob.upload_from_file(data, size=size, retry=DEFAULT_RETRY)
            else:
                # vivi uses utf-8 encoding throughout, see
                # zeit.cms.content.adapter for XML and zeit.content.text.text
                content.body = resource.data.read().decode('utf-8')

        if uniqueid in self.property_cache:
            self.property_cache[uniqueid] = content
            resource.data.seek(0)
            self.body_cache[uniqueid] = resource.data.read()

    def changeProperties(self, uniqueid, properties):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        current = content.to_webdav()
        current.update(properties)
        content.from_webdav(current)
        if uniqueid in self.property_cache:
            self.property_cache[uniqueid] = content

    def __delitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        if content.is_collection and self._foreign_child_lock_exists(uniqueid):
            raise LockedByOtherSystemError(
                uniqueid, f'Could not delete {uniqueid}, because it is locked.'
            )
        if not content.is_collection and content.binary_body:
            blob = self.bucket.blob(content.id)
            with zeit.cms.tracing.use_span(
                __name__ + '.tracing',
                'gcs',
                attributes={'db.operation': 'delete', 'id': content.id},
            ):
                try:
                    blob.delete()
                except google.api_core.exceptions.NotFound:
                    log.info('Ignored NotFound while deleting GCS blob %s', uniqueid)

        self.unlock(uniqueid)
        if content.is_collection:
            (parent, _) = self._pathkey(uniqueid)
            stmt = delete(Path).where(Path.parent_path.startswith(parent))
            self.session.execute(stmt)
        else:
            self.session.delete(content)

        self.property_cache.pop(uniqueid, None)
        self.body_cache.pop(uniqueid, None)

    @staticmethod
    def _normalize(uniqueid):
        if not uniqueid.startswith(ID_NAMESPACE):
            raise ValueError(f'The id {uniqueid} is invalid.')
        return uniqueid.rstrip('/')

    @staticmethod
    def _pathkey(uniqueid):
        (parent_path, name) = os.path.split(uniqueid.replace(ID_NAMESPACE, '', 1))
        parent_path = parent_path.rstrip('/')
        return (parent_path, name)

    def copy(self, old_id, new_id):
        old_id = self._normalize(old_id)
        new_id = self._normalize(new_id)
        if new_id in self:
            raise CopyError(
                old_id,
                f'Could not copy {old_id} to {new_id}, because target already exists.',
            )
        old_resource = self[old_id]
        old_content = self._get_content(old_id)
        new_content = Content()
        new_content.unsorted = old_content.unsorted
        new_resource = Resource(
            new_id,
            new_id.split('/')[-1],
            old_resource.type,
            old_resource.data,
            new_content.to_webdav_attributes(),
            old_resource.contentType,
        )
        self[new_id] = new_resource
        if old_content.is_collection:
            for name, _ in self.listCollection(old_id):
                self.copy(f'{old_id}/{name}', f'{new_id}/{name}')

    def move(self, old_id, new_id):
        old_id = self._normalize(old_id)
        new_id = self._normalize(new_id)
        content = self._get_content(old_id)
        if content is None:
            raise KeyError(f'The resource {old_id} does not exist.')
        if new_id in self:
            raise MoveError(
                old_id, f'Could not move {old_id} to {new_id}, because target already exists.'
            )
        if content.is_collection:
            if self._foreign_child_lock_exists(old_id):
                raise LockedByOtherSystemError(
                    old_id, f'Could not move {old_id} to {new_id}, because it is locked.'
                )
            for name, _ in self.listCollection(old_id):
                self.move(f'{old_id}/{name}', f'{new_id}/{name}')

        path = self.session.get(Path, self._pathkey(old_id))
        (path.parent_path, path.name) = self._pathkey(new_id)
        # unlock checks if locked and unlocks if necessary
        self.unlock(new_id)

        self.property_cache.pop(old_id, None)
        self.body_cache.pop(old_id, None)

    def _foreign_child_lock_exists(self, id):
        (parent, _) = self._pathkey(id)
        locks = self.session.query(Lock).filter(Lock.parent_path.startswith(parent)).all()
        return any([not self._is_current_principal(lock.principal) for lock in locks])

    def _get_lock_status(self, id):
        lock_principal, until, is_my_lock = self.locked(id)
        if lock_principal is None and until is None:
            return LockStatus.NO_LOCK
        elif is_my_lock:
            return LockStatus.OWN_LOCK
        else:
            return LockStatus.OTHERS_LOCK

    def _add_lock(self, id, principal, until):
        path = self.session.get(Path, self._pathkey(id))
        if path is None:
            log.warning('Unable to add lock to resource %s that does not exist.', str(id))
            return
        stmt = Lock.create(path=path, principal=principal, until=until)
        self.session.execute(stmt)
        return self.session.get(Lock, (path.parent_path, path.name, path.id)).token

    def _is_current_principal(self, principal):
        # Let's see if the principal is one we know.
        try:
            import zope.authentication.interfaces  # UI-only dependency

            authentication = zope.component.queryUtility(
                zope.authentication.interfaces.IAuthentication
            )
        except ImportError:
            authentication = None
        if authentication is not None:
            try:
                authentication.getPrincipal(principal)
            except zope.authentication.interfaces.PrincipalLookupError:
                pass
            else:
                return True
        return False

    def lock(self, id, principal, until):
        match self._get_lock_status(id):
            case LockStatus.NO_LOCK:
                return self._add_lock(id, principal, until)
            case LockStatus.OWN_LOCK:
                raise LockingError(id, f'You already own the lock of {id}.')
            case LockStatus.OTHERS_LOCK:
                raise LockedByOtherSystemError(id, f'{id} is already locked.')

    def unlock(self, id):
        path = self.session.get(Path, self._pathkey(id))
        if path is None:
            raise KeyError(f'The resource {id} does not exist.')
        lock = self.session.get(Lock, (path.parent_path, path.name, path.id))
        if not lock:
            return
        if not self._is_current_principal(lock.principal):
            raise LockedByOtherSystemError(id, f'{id} is already locked.')
        self.session.delete(lock)

    def _unlock(self, id, token):
        path = self.session.get(Path, self._pathkey(id))
        if path is None:
            raise KeyError(f'The resource {id} does not exist.')
        lock = self.session.get(Lock, (path.parent_path, path.name, path.id))
        if not lock or not lock.token == token:
            return
        self.session.delete(lock)

    def locked(self, id):
        path = self.session.get(Path, self._pathkey(id))
        if path is None:
            log.warning('The resource %s does not exist.', str(id))
            return (None, None, False)
        lock = self.session.get(Lock, (path.parent_path, path.name, path.id))
        if lock is None:
            return (None, None, False)
        is_my_lock = self._is_current_principal(lock.principal)

        return (lock.principal, lock.until, is_my_lock)

    def search(self, attrlist, expr):
        if (
            len(attrlist) == 1
            and attrlist[0].name == 'uuid'
            and attrlist[0].namespace == DOCUMENT_SCHEMA_NS
        ):
            # Sorely needed performance optimization.
            uuid = expr.operands[-1].replace('urn:uuid:', '')
            result = self.session.execute(
                select(Path.id, Path.parent_path, Path.name).filter_by(id=uuid)
            )
            for item in result:
                yield (f'{ID_NAMESPACE}{item.parent_path}/{item.name}', item.id)
        else:
            query = select(Path).join(Content).filter(_build_filter(expr))
            result = self.session.execute(query)
            itemgetters = [
                (itemgetter(a.namespace.replace(Content.NS, '', 1)), itemgetter(a.name))
                for a in attrlist
            ]
            for item in result.scalars():
                for nsgetter, keygetter in itemgetters:
                    value = keygetter(nsgetter(item.content.unsorted))
                    yield (f'{ID_NAMESPACE}{item.parent_path}/{item.name}', value)


factory = Connector.factory


METADATA = sqlalchemy.MetaData()
DBObject = sqlalchemy.orm.declarative_base(metadata=METADATA)


class Path(DBObject):
    __tablename__ = 'paths'
    __table_args__ = (UniqueConstraint('parent_path', 'name', 'id'),)

    parent_path = Column(Unicode, primary_key=True, index=True)
    name = Column(Unicode, primary_key=True)

    id = Column(
        Uuid(as_uuid=False),
        ForeignKey('properties.id', ondelete='cascade'),
        nullable=False,
        index=True,
    )
    content = relationship(
        'Content',
        uselist=False,
        lazy='joined',
        backref=backref('path', uselist=False, cascade='all, delete-orphan', passive_deletes=True),
    )


class Lock(DBObject):
    __tablename__ = 'locks'

    parent_path = Column(Unicode, primary_key=True)
    name = Column(Unicode, primary_key=True)
    id = Column(Uuid(as_uuid=False), primary_key=True)
    principal = Column(Unicode, nullable=False)
    until = Column(TIMESTAMP(timezone=True), nullable=False)

    __table_args__ = (
        schema.ForeignKeyConstraint(
            (parent_path, name, id), (Path.parent_path, Path.name, Path.id), onupdate='CASCADE'
        ),
    )

    @classmethod
    def create(cls, path, principal, until):
        stmt = insert(cls).values(
            parent_path=path.parent_path,
            name=path.name,
            id=path.id,
            principal=principal,
            until=until,
        )
        return stmt

    @property
    def token(self):
        "Backwards compatibility with DAV backend which returns a token if a lock was added."
        return hashlib.sha256(f'{self.principal}{self.id}'.encode('utf-8')).hexdigest()


class Content(DBObject):
    __tablename__ = 'properties'

    id = Column(Uuid(as_uuid=False), primary_key=True)
    type = Column(Unicode, nullable=False, server_default='unknown')
    is_collection = Column(Boolean, nullable=False, server_default='false')

    body = Column(UnicodeText)

    unsorted = Column(JSONB)

    last_updated = Column(
        TIMESTAMP(timezone=True),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )

    @property
    def binary_body(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        binary_types = config.get('binary-types', 'image,file,unknown').split(',')
        return self.type in binary_types

    NS = 'http://namespaces.zeit.de/CMS/'

    def to_webdav_attributes(self):
        props = {}
        for ns, d in self.unsorted.items():
            for k, v in d.items():
                props[(k, self.NS + ns)] = v
        return props

    def to_webdav(self):
        props = self.to_webdav_attributes()

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
            if v is DeleteProperty:
                continue
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
            self.upstream = zeit.connector.zopeconnector.ZopeConnector({'default': repository_path})
        else:
            self.upstream = zeit.connector.filesystem.Connector(repository_path)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product

        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        return cls(
            config['dsn'],
            config['storage-project'],
            config['storage-bucket'],
            config['repository-path'],
        )

    def __getitem__(self, id):
        try:
            return super().__getitem__(id)
        except KeyError:
            return self._import(id)

    def _import(self, id):
        log.debug('_import %s', id)
        resource = self.upstream[id]
        # Hacky. Remove this as it is not json-serializable, and also
        # irrelevant except for DAV caches.
        resource.content.data.pop(('cached-time', 'INTERNAL'), None)
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


class EngineTracer(opentelemetry.instrumentation.sqlalchemy.EngineTracer):
    def __init__(self, engine, **kw):
        tracer = self  # Kludge to inject zeit.cms.tracing.start_span()
        meter = opentelemetry.metrics.get_meter(
            __name__,
            'unused',
        )
        unused_metrics = meter.create_up_down_counter('unused')
        super().__init__(tracer, engine, unused_metrics, **kw)

    def start_span(self, *args, **kw):
        return zeit.cms.tracing.start_span(__name__ + '.tracing', *args, **kw)

    def _write(self, buffer, params):
        for k, v in params.items():
            buffer.write('%s=%r\n' % (k, str(v)[:100]))

    def _before_cur_exec(self, conn, cursor, statement, params, context, executemany):
        statement, params = super()._before_cur_exec(
            conn, cursor, statement, params, context, executemany
        )
        p = StringIO()
        if isinstance(params, (list, tuple)):
            for param in params:
                self._write(p, param)
        elif isinstance(params, dict):
            self._write(p, params)
        context._otel_span.set_attribute('db.parameters', p.getvalue())
        return statement, params
