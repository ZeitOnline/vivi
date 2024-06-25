from ast import literal_eval
from datetime import datetime, timedelta
from enum import Enum
from functools import partial
from io import BytesIO, StringIO
from logging import getLogger
from uuid import uuid4
import collections
import hashlib
import itertools
import json
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
    Index,
    Unicode,
    UnicodeText,
    UniqueConstraint,
    Uuid,
    bindparam,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import joinedload, relationship
import google.api_core.exceptions
import opentelemetry.instrumentation.sqlalchemy
import opentelemetry.metrics
import pytz
import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm
import transaction
import zope.component
import zope.interface
import zope.sqlalchemy

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.cms.repository.interfaces import ConflictError
from zeit.connector.interfaces import (
    INTERNAL_PROPERTY,
    CopyError,
    DeleteProperty,
    LockedByOtherSystemError,
    LockingError,
    MoveError,
)
from zeit.connector.lock import lock_is_foreign
import zeit.cms.cli
import zeit.cms.interfaces
import zeit.cms.tracing
import zeit.connector.cache
import zeit.connector.interfaces
import zeit.connector.resource


log = getLogger(__name__)


ID_NAMESPACE = zeit.connector.interfaces.ID_NAMESPACE[:-1]


class LockStatus(Enum):
    NONE = 0
    FOREIGN = 1
    OWN = 2
    TIMED_OUT = 3


@zope.interface.implementer(zeit.connector.interfaces.ICachingConnector)
class Connector:
    resource_class = zeit.connector.resource.CachedResource

    def __init__(
        self,
        dsn,
        storage_project,
        storage_bucket,
        reconnect_tries=3,
        reconnect_wait=0.1,
        support_locking=False,
    ):
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
        self.support_locking = support_locking

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
        params['support_locking'] = literal_eval(config.get('sql-locking', 'False'))
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
        properties = self._get_properties(uniqueid)  # may raise KeyError
        return self.resource_class(
            uniqueid,
            uniqueid.split('/')[-1],
            properties.get(('type', Content.NS + 'meta'), 'unknown'),
            lambda: properties,
            partial(self._get_body, uniqueid),
            is_collection=properties[('is_collection', INTERNAL_PROPERTY)],
        )

    property_cache = TransactionBoundCache('_v_property_cache', zeit.connector.cache.PropertyCache)

    def _get_properties(self, uniqueid):
        if uniqueid == ID_NAMESPACE:
            content = Content(id='root', type='folder', is_collection=True, unsorted={})
            return content.to_webdav()

        if uniqueid in self.property_cache:
            return self.property_cache[uniqueid]

        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        properties = content.to_webdav()
        self.property_cache[uniqueid] = properties
        return properties

    body_cache = TransactionBoundCache('_v_body_cache', zeit.connector.cache.ResourceCache)

    def _get_body(self, uniqueid):
        if uniqueid == ID_NAMESPACE:
            return BytesIO(b'')

        if uniqueid in self.body_cache:
            return self.body_cache[uniqueid]

        content = self._get_content(uniqueid, getlock=False)
        if content.is_collection:
            body = b''
        elif content.binary_body:
            body = self._get_binary_body(content.id)
        elif not content.body:
            body = b''
        else:
            body = content.body.encode('utf-8')

        body = BytesIO(body)
        body = self.body_cache.update(uniqueid, body)
        return body

    def _get_binary_body(self, id):
        blob = self.bucket.blob(id)
        with zeit.cms.tracing.use_span(
            __name__ + '.tracing', 'gcs', attributes={'db.operation': 'download', 'id': id}
        ):
            body = blob.download_as_bytes()
        return body

    def __contains__(self, uniqueid):
        try:
            self[uniqueid]
            return True
        except KeyError:
            return False

    child_name_cache = TransactionBoundCache(
        '_v_child_name_cache', zeit.connector.cache.ChildNameCache
    )

    def listCollection(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        if uniqueid != ID_NAMESPACE and uniqueid not in self:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        if uniqueid not in self.child_name_cache:
            self._reload_child_name_cache(uniqueid)
        for child in list(self.child_name_cache[uniqueid]):
            yield (self._pathkey(child)[1], child)

    def _reload_child_name_cache(self, uniqueid):
        if uniqueid == ID_NAMESPACE:
            parent_path = ''
        else:
            if self._get_content(uniqueid, getlock=False) is None:
                self.child_name_cache.pop(uniqueid, None)
                return
            parent_path = '/'.join(self._pathkey(uniqueid))
        result = [
            (x.name, x.uniqueid)
            for x in self.session.execute(select(Path).filter_by(parent_path=parent_path)).scalars()
        ]
        self.child_name_cache[uniqueid] = set(x[1] for x in result)

    def _update_parent_child_name_cache(self, uniqueid, operation):
        parent = os.path.split(uniqueid)[0]
        cached = self.child_name_cache.get(parent)
        if cached is not None:
            operation = getattr(cached, operation)
            operation(uniqueid)

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
            if content.lock_status == LockStatus.FOREIGN:
                raise LockedByOtherSystemError(uniqueid, f'{uniqueid} is already locked.')

        (path.parent_path, path.name) = self._pathkey(uniqueid)
        current = content.to_webdav()

        if not FEATURE_TOGGLES.find('disable_connector_body_checksum') and verify_etag and exists:
            current_checksum = current[('body_checksum', INTERNAL_PROPERTY)]
            new_checksum = resource.properties.get(('body_checksum', INTERNAL_PROPERTY))
            if new_checksum is not None and current_checksum != new_checksum:
                raise ConflictError(
                    uniqueid,
                    f'{uniqueid} body has changed. New checksum {new_checksum} '
                    f'does not match stored checksum {current_checksum}.',
                )

        current.update(resource.properties)
        content.from_webdav(current)
        content.type = resource.type
        content.is_collection = resource.is_collection

        if not content.is_collection:
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

        self.property_cache[uniqueid] = content.to_webdav()
        if content.is_collection:
            self._reload_child_name_cache(uniqueid)
        parent = os.path.split(uniqueid)[0]
        self._reload_child_name_cache(parent)
        self.body_cache.pop(uniqueid, None)

    def changeProperties(self, uniqueid, properties):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        if content.lock_status == LockStatus.FOREIGN:
            raise LockedByOtherSystemError(uniqueid, f'{uniqueid} is already locked.')
        current = content.to_webdav()
        current.update(properties)
        content.from_webdav(current)
        self.property_cache[uniqueid] = content.to_webdav()

    def __delitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        # unlock checks if locked and unlocks if necessary
        self.unlock(uniqueid)

        to_delete = [content]
        if content.is_collection:
            to_delete.extend(self._get_all_children(content.uniqueid))

            for child in to_delete:
                if child.lock and lock_is_foreign(child.lock.principal):
                    raise LockedByOtherSystemError(
                        child.uniqueid, f'Could not delete {child.uniqueid}, because it is locked.'
                    )

        for content in to_delete:
            self.property_cache.pop(content.uniqueid, None)
            self.body_cache.pop(content.uniqueid, None)
            self.child_name_cache.pop(content.uniqueid, None)
            self._update_parent_child_name_cache(content.uniqueid, 'remove')

        responses = self._gcs_batch(
            'delete',
            [x.id for x in to_delete if x.binary_body],
            lambda id: self.bucket.delete_blob(id),
        )
        for id, response in zip(to_delete, responses):
            if 200 <= response.status_code < 300:
                continue
            if response.status_code == 404:
                log.info('Ignored NotFound while deleting GCS blob %s', id)
                continue
            raise google.cloud.exceptions.from_http_response(response)

        self.session.execute(delete(Content).where(Content.id.in_([x.id for x in to_delete])))

    def _get_all_children(self, uniqueid):
        parent = uniqueid.replace(ID_NAMESPACE, '', 1)
        query = (
            select(Content)
            .join(Path)
            .where(Path.parent_path.startswith(parent))
            .order_by(Path.parent_path)
        )
        query = query.options(joinedload(Content.lock))
        return self.session.execute(query).scalars()

    def _gcs_batch(self, span_name, ids, function):
        responses = []
        if not ids:
            return responses
        with zeit.cms.tracing.use_span(
            __name__ + '.tracing',
            'gcs',
            attributes={'db.operation': span_name, 'ids': ids},
        ):
            for chunk in batched(ids, google.cloud.storage.batch.Batch._MAX_BATCH_SIZE - 1):
                # We'd rather use the official `with client.batch()` API, but
                # that does not return responses with raise_exception=False.
                batch = self.gcs_client.batch()
                self.gcs_client._push_batch(batch)
                for item in chunk:
                    function(item)
                responses.extend(batch.finish(raise_exception=False))
                self.gcs_client._pop_batch()
        return responses

    def _get_content(self, uniqueid, getlock=True):
        parent, name = self._pathkey(uniqueid)
        query = select(Path).filter_by(parent_path=parent, name=name)
        if getlock and self.support_locking:
            query = query.options(joinedload(Path.content).joinedload(Content.lock))
        path = self.session.execute(query).scalars().one_or_none()
        return path.content if path is not None else None

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

    def copy(self, old_uniqueid, new_uniqueid):
        old_uniqueid = self._normalize(old_uniqueid)
        new_uniqueid = self._normalize(new_uniqueid)
        if new_uniqueid in self:
            raise CopyError(
                old_uniqueid,
                f'Could not copy {old_uniqueid} to {new_uniqueid}, because target already exists.',
            )
        content = self._get_content(old_uniqueid)
        if content is None:
            raise KeyError(f'The resource {old_uniqueid} does not exist.')

        sources = [content]
        if content.is_collection:
            sources.extend(self._get_all_children(content.uniqueid))

        targets = []
        binary = []
        for content in sources:
            target = self._clone_row(content, ['id', 'last_updated'])
            target.id = str(uuid4())

            uniqueid = content.uniqueid.replace(old_uniqueid, new_uniqueid)
            (parent_path, name) = self._pathkey(uniqueid)
            target.path = Path(id=target.id, parent_path=parent_path, name=name)
            targets.append(target)

            if content.binary_body:
                binary.append((content.id, target.id))

        responses = self._gcs_batch(
            'copy',
            binary,
            lambda x: self.bucket.copy_blob(
                self.bucket.blob(x[0]), self.bucket, x[1], retry=DEFAULT_RETRY
            ),
        )
        for response in responses:
            if 200 <= response.status_code < 300:
                continue
            raise google.cloud.exceptions.from_http_response(response)

        self._bulk_insert(Content, targets)
        self._bulk_insert(Path, [x.path for x in targets])

        for content in targets:
            self.property_cache[content.uniqueid] = content.to_webdav()
            if content.is_collection:
                self.child_name_cache[content.uniqueid] = set()
            self._update_parent_child_name_cache(content.uniqueid, 'add')

    def _clone_row(self, row, ignored_columns=()):
        cls = type(row)
        clone = cls()
        for column in self._columns(cls):
            if column not in ignored_columns:
                setattr(clone, column, getattr(row, column))
        return clone

    def _bulk_insert(self, cls, items):
        self.session.execute(
            insert(cls), [{c: getattr(x, c) for c in self._columns(cls)} for x in items]
        )

    @staticmethod
    def _columns(cls):
        return [c.key for c in sqlalchemy.orm.class_mapper(cls).columns]

    def move(self, old_uniqueid, new_uniqueid):
        old_uniqueid = self._normalize(old_uniqueid)
        new_uniqueid = self._normalize(new_uniqueid)
        content = self._get_content(old_uniqueid)
        if content is None:
            raise KeyError(f'The resource {old_uniqueid} does not exist.')
        if new_uniqueid in self:
            raise MoveError(
                old_uniqueid,
                f'Could not move {old_uniqueid} to {new_uniqueid}, because target already exists.',
            )
        if content.lock:
            if lock_is_foreign(content.lock.principal):
                raise LockedByOtherSystemError(old_uniqueid, f'{old_uniqueid} is already locked.')
            del content.lock

        sources = [content]
        if content.is_collection:
            sources.extend(self._get_all_children(content.uniqueid))

            for child in sources:
                if child.lock and lock_is_foreign(child.lock.principal):
                    raise LockedByOtherSystemError(
                        old_uniqueid,
                        f'Could not move {child.uniqueid} to {new_uniqueid}, because it is locked.',
                    )

        updates = []
        for content in sources:
            source_uniqueid = content.uniqueid
            target_uniqueid = source_uniqueid.replace(old_uniqueid, new_uniqueid)
            parent, name = self._pathkey(target_uniqueid)
            updates.append({'key': content.id, 'parent_path': parent, 'name': name})

            self.property_cache.pop(source_uniqueid, None)
            self.property_cache[target_uniqueid] = content.to_webdav()
            self.body_cache.pop(source_uniqueid, None)
            if content.is_collection:
                self.child_name_cache.pop(source_uniqueid, None)
                self.child_name_cache[target_uniqueid] = set()
            self._update_parent_child_name_cache(source_uniqueid, 'remove')
            self._update_parent_child_name_cache(target_uniqueid, 'add')

        # We're updating the primary key itself, which the normal sqlalchemy
        # "bulk update " API does not offer, so we have to user a lower level,
        # <https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html
        #  #disabling-bulk-orm-update-by-primary-key-for-an-update-statement
        #  -with-multiple-parameter-sets>
        self.session.connection().execute(update(Path).where(Path.id == bindparam('key')), updates)
        zope.sqlalchemy.mark_changed(self.session())

    def lock(self, uniqueid, principal, until):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        match content.lock_status:
            case LockStatus.NONE | LockStatus.TIMED_OUT:
                lock = content.lock
                if not lock:
                    lock = Lock(id=content.id)
                    self.session.add(lock)
                lock.principal = principal
                if until is None:
                    until = datetime.now(pytz.UTC) + timedelta(hours=1)
                lock.until = until
                content.lock = lock
                self._update_lock_cache(content.uniqueid, principal, until)
                return lock.token
            case LockStatus.OWN:
                raise LockingError(id, f'You already own the lock of {uniqueid}.')
            case LockStatus.FOREIGN:
                raise LockedByOtherSystemError(uniqueid, f'{uniqueid} is already locked.')

    def unlock(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        lock = self._get_content(uniqueid).lock
        if not lock:
            return
        if lock_is_foreign(lock.principal):
            raise LockedByOtherSystemError(uniqueid, f'{uniqueid} is already locked.')
        self.session.delete(lock)
        self._update_lock_cache(uniqueid, None)

    def _unlock(self, uniqueid, token):
        uniqueid = self._normalize(uniqueid)
        lock = self._get_content(uniqueid).lock
        if not lock or not lock.token == token:
            return
        self.session.delete(lock)
        self._update_lock_cache(uniqueid, None)

    def _update_lock_cache(self, uniqueid, principal, until=None):
        properties = self._get_properties(uniqueid)
        properties[('lock_principal', INTERNAL_PROPERTY)] = principal
        if until is None:
            properties.pop(('lock_until', INTERNAL_PROPERTY), None)
        else:
            properties[('lock_until', INTERNAL_PROPERTY)] = until
        self.property_cache[uniqueid] = properties

    def locked(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        lock = self._get_cached_lock(uniqueid)
        match lock.status:
            case LockStatus.NONE | LockStatus.TIMED_OUT:
                return (None, None, False)
            case LockStatus.OWN:
                return (lock.principal, lock.until, True)
            case LockStatus.FOREIGN:
                return (lock.principal, lock.until, False)
            case _:
                return (None, None, False)

    def _get_cached_lock(self, uniqueid):
        properties = self._get_properties(uniqueid)
        return Lock(
            principal=properties.get(('lock_principal', INTERNAL_PROPERTY)),
            until=properties.get(('lock_until', INTERNAL_PROPERTY)),
        )

    def search(self, attrlist, expr):
        if (
            len(attrlist) == 1
            and attrlist[0].name == 'uuid'
            and attrlist[0].namespace == DOCUMENT_SCHEMA_NS
        ):
            # Sorely needed performance optimization.
            uuid = expr.operands[-1].replace('urn:uuid:', '')
            path = self.session.execute(select(Path).where(Path.id == uuid)).scalar()
            if path is not None:
                yield (path.uniqueid, '{urn:uuid:%s}' % path.id)
        else:
            query = select(Content).where(self._build_filter(expr))
            result = self.session.execute(query)
            for item in result.scalars():
                data = [item.uniqueid]
                properties = item.to_webdav()
                data.extend([properties[(a.name, a.namespace)] for a in attrlist])
                yield tuple(data)

    def _build_filter(self, expr):
        op = expr.operator
        if op == 'and':
            return sqlalchemy.and_(*(self._build_filter(e) for e in expr.operands))
        elif op == 'eq':
            (var, value) = expr.operands
            name = var.name
            namespace = var.namespace.replace(Content.NS, '', 1)
            value = json.dumps(str(value))  # Apply correct quoting for jsonpath.
            return Content.unsorted.path_match(f'$.{namespace}.{name} == {value}')
        else:
            raise RuntimeError(f'Unknown operand {op!r} while building search query')

    def invalidate_cache(self, uniqueid):
        content = self._get_content(uniqueid)
        if content is None:
            self.property_cache.pop(uniqueid, None)
            self.child_name_cache.pop(uniqueid, None)
        else:
            self.property_cache[uniqueid] = content.to_webdav()
            if content.is_collection:
                self._reload_child_name_cache(uniqueid)
        parent = os.path.split(uniqueid)[0]
        self._reload_child_name_cache(parent)
        self.body_cache.pop(uniqueid, None)


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
    content = relationship('Content', uselist=False, lazy='joined', back_populates='path')

    @property
    def uniqueid(self):
        return f'{ID_NAMESPACE}{self.parent_path}/{self.name}'


class Content(DBObject):
    __tablename__ = 'properties'
    __table_args__ = (
        Index(
            f'ix_{__tablename__}_unsorted',
            'unsorted',
            postgresql_using='gin',
            postgresql_ops={'unsorted': 'jsonb_path_ops'},
        ),
    )

    id = Column(Uuid(as_uuid=False), primary_key=True)
    type = Column(Unicode, nullable=False, server_default='unknown', index=True)
    is_collection = Column(Boolean, nullable=False, server_default='false')

    body = Column(UnicodeText)

    unsorted = Column(JSONB)

    last_updated = Column(
        TIMESTAMP(timezone=True),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        index=True,
    )

    path = relationship(
        'Path',
        uselist=False,
        lazy='joined',
        back_populates='content',
        cascade='all, delete-orphan',
        passive_deletes=True,  # Handled in DB, Path.id has ondelete=cascade
    )
    lock = relationship(
        'Lock',
        uselist=False,
        lazy='noload',
        back_populates='content',
        cascade='delete, delete-orphan',  # Propagate `del content.lock` to DB
        passive_deletes=True,  # Disable any heuristics, only ever explicitly delete Locks
    )

    @property
    def binary_body(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.connector') or {}
        binary_types = config.get('binary-types', 'image,file,unknown').split(',')
        return self.type in binary_types

    @property
    def uniqueid(self):
        return self.path.uniqueid

    @property
    def lock_status(self):
        return self.lock.status if self.lock else LockStatus.NONE

    NS = 'http://namespaces.zeit.de/CMS/'

    def to_webdav(self):
        if self.unsorted is None:
            return {}

        props = {}
        for ns, d in self.unsorted.items():
            for k, v in d.items():
                props[(k, self.NS + ns)] = v

        props[('uuid', self.NS + 'document')] = '{urn:uuid:%s}' % self.id
        props[('type', self.NS + 'meta')] = self.type
        props[('is_collection', INTERNAL_PROPERTY)] = self.is_collection
        props[('body_checksum', INTERNAL_PROPERTY)] = self._body_checksum()

        if self.lock:
            props[('lock_principal', INTERNAL_PROPERTY)] = self.lock.principal
            props[('lock_until', INTERNAL_PROPERTY)] = self.lock.until
        else:
            props[('lock_principal', INTERNAL_PROPERTY)] = None

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

        type = props.get(('type', self.NS + 'meta'))
        if type:
            self.type = type

        unsorted = collections.defaultdict(dict)
        for (k, ns), v in props.items():
            if v is DeleteProperty:
                continue
            if ns == INTERNAL_PROPERTY:
                continue
            unsorted[ns.replace(self.NS, '', 1)][k] = v
        self.unsorted = unsorted

    def _body_checksum(self):
        # Excluding binary_body here trades off correctness for performance.
        # We assume that editing binary content types happens only rarely,
        # and thus can do without the additional conflict protection.
        if self.is_collection or not self.body or self.binary_body:
            return None
        alg = hashlib.sha256(usedforsecurity=False)
        alg.update(self.body.encode('utf-8'))
        return alg.hexdigest()


class Lock(DBObject):
    __tablename__ = 'locks'

    id = Column(Uuid(as_uuid=False), ForeignKey('properties.id'), primary_key=True)
    principal = Column(Unicode, nullable=False)
    until = Column(TIMESTAMP(timezone=True), nullable=False)

    content = relationship('Content', uselist=False, lazy='noload', back_populates='lock')

    @property
    def token(self):
        "Backwards compatibility with DAV backend which returns a token if a lock was added."
        return hashlib.sha256(f'{self.principal}{self.id}'.encode('utf-8')).hexdigest()

    @property
    def status(self):
        if self.principal is None and self.until is None:
            return LockStatus.NONE
        elif self.until < datetime.now(pytz.UTC):
            return LockStatus.TIMED_OUT
        elif not lock_is_foreign(self.principal):
            return LockStatus.OWN
        else:
            return LockStatus.FOREIGN


def batched(iterable, n):
    """Batch data into tuples of length n. The last batch may be shorter.
    Example: `batched('ABCDEFG', 3) --> ABC DEF G`
    Backport from Python-3.12, see stdlib itertools recipes.
    """
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := list(itertools.islice(it, n)):
        yield batch


class SQLZopeConnector(Connector):
    @property
    def property_cache(self):
        return zope.component.getUtility(zeit.connector.interfaces.IPropertyCache)

    @property
    def child_name_cache(self):
        return zope.component.getUtility(zeit.connector.interfaces.IChildNameCache)

    @property
    def body_cache(self):
        return zope.component.getUtility(zeit.connector.interfaces.IResourceCache)

    def invalidate_cache(self, uniqueid):
        zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(uniqueid))
        # actual invalidation is performed by `invalidate_cache` event handler

    def _invalidate_cache(self, uniqueid):
        super().invalidate_cache(uniqueid)


@zope.component.adapter(zeit.connector.interfaces.IResourceInvalidatedEvent)
def invalidate_cache(event):
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    connector._invalidate_cache(event.id)


zope_factory = SQLZopeConnector.factory


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


def _unlock_overdue_locks():
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    if not isinstance(connector, Connector):
        log.debug('Not SQL connector, skipping lock cleanup')
        return
    log.info('Unlock overdue locks...')
    stmt = delete(Lock).where(Lock.until < datetime.now(pytz.UTC))
    connector.session.execute(stmt)
    transaction.commit()


@zeit.cms.cli.runner()
def unlock_overdue_locks():
    _unlock_overdue_locks()
