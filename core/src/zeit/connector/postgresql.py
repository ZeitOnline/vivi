from ast import literal_eval
from functools import partial
from io import BytesIO, StringIO
from logging import getLogger
from uuid import uuid4
import itertools
import json
import os
import os.path
import pkgutil
import time

from gocept.cache.property import TransactionBoundCache
from google.cloud import storage
from google.cloud.storage.retry import DEFAULT_RETRY
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import joinedload
import google.api_core.exceptions
import opentelemetry.instrumentation.sqlalchemy
import opentelemetry.metrics
import pendulum
import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm
import transaction
import zope.component
import zope.interface
import zope.sqlalchemy

from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
from zeit.cms.repository.interfaces import ConflictError
from zeit.connector.interfaces import (
    INTERNAL_PROPERTY,
    CopyError,
    LockedByOtherSystemError,
    LockingError,
    LockStatus,
    MoveError,
)
from zeit.connector.models import ID_NAMESPACE, Content, Lock
import zeit.cms.cli
import zeit.cms.config
import zeit.cms.interfaces
import zeit.cms.tracing
import zeit.connector.cache
import zeit.connector.interfaces
import zeit.connector.resource


log = getLogger(__name__)


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
        pool_class=None,
    ):
        self.dsn = dsn
        self.reconnect_tries = reconnect_tries
        self.reconnect_wait = reconnect_wait
        self.engine = sqlalchemy.create_engine(dsn, poolclass=pool_class)
        sqlalchemy.event.listen(self.engine, 'engine_connect', self._reconnect)
        sqlalchemy.event.listen(
            self.engine, 'before_cursor_execute', self._set_statement_timeout, retval=True
        )
        self.session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=self.engine))
        zope.sqlalchemy.register(self.session)
        EngineTracer(self.engine, enable_commenter=True)
        self.gcs_client = storage.Client(project=storage_project)
        self.bucket = self.gcs_client.bucket(storage_bucket)
        self.support_locking = support_locking

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        config = zeit.cms.config.package('zeit.connector')
        params = {}
        reconnect_tries = config.get('sql-reconnect-tries')
        if reconnect_tries is not None:
            params['reconnect_tries'] = int(reconnect_tries)
        reconnect_wait = config.get('sql-reconnect-wait')
        if reconnect_wait is not None:
            params['reconnect_wait'] = float(reconnect_wait)
        params['support_locking'] = literal_eval(config.get('sql-locking', 'False'))
        pool = config.get('sql-pool-class')
        if pool:
            params['pool_class'] = pkgutil.resolve_name(pool)
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

    # Adapted from https://github.com/sqlalchemy/sqlalchemy/discussions/8193
    @staticmethod
    def _set_statement_timeout(conn, cursor, statement, parameters, context, executemany):
        timeout = context.execution_options.get('statement_timeout')
        if timeout is not None:
            cursor.execute('SET LOCAL statement_timeout=%s', (timeout,))
        return (statement, parameters)

    def resource(self, uniqueid, properties):
        return self.resource_class(
            uniqueid,
            uniqueid.split('/')[-1],
            properties.get(('type', Content.NS + 'meta'), 'unknown'),
            lambda: properties,
            partial(self._get_body, uniqueid),
            is_collection=properties[('is_collection', INTERNAL_PROPERTY)],
        )

    def __getitem__(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        # may raise KeyError
        properties = self._get_properties(uniqueid, update_body_cache=True)
        return self.resource(uniqueid, properties)

    property_cache = TransactionBoundCache('_v_property_cache', zeit.connector.cache.PropertyCache)

    def _get_properties(self, uniqueid, update_body_cache=False):
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
        # Performance optimization: Until WCM-10 lands, non-binary body is
        # always parsed on ICMSContent conversion, and thus we always load the
        # column anyway. So we might as well put it in the cache right here,
        # instead of performing an extra query shortly afterwards in _get_body().
        if update_body_cache:
            self._update_body_cache(uniqueid, content)
        return properties

    body_cache = TransactionBoundCache('_v_body_cache', zeit.connector.cache.ResourceCache)

    def _get_body(self, uniqueid):
        if uniqueid == ID_NAMESPACE:
            return BytesIO(b'')

        if uniqueid in self.body_cache:
            return self.body_cache[uniqueid]

        content = self._get_content(uniqueid, getlock=False)
        return self._update_body_cache(uniqueid, content, load_binary=True)

    def _update_body_cache(self, uniqueid, content, load_binary=False):
        if content.is_collection:
            body = b''
        elif content.binary_body:
            if not load_binary:
                return None
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
            parent = ''
        else:
            if self._get_content(uniqueid, getlock=False) is None:
                self.child_name_cache.pop(uniqueid, None)
                return
            parent = '/'.join(self._pathkey(uniqueid))
        result = self.session.execute(select(Content).filter_by(parent_path=parent))
        self.child_name_cache[uniqueid] = set(x.uniqueid for x in result.scalars())

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
            self.session.add(content)
        else:
            if content.lock_status == LockStatus.FOREIGN:
                raise LockedByOtherSystemError(
                    uniqueid, f'{uniqueid} is already locked by {content.lock.principal}'
                )

        (content.parent_path, content.name) = self._pathkey(uniqueid)
        current = content.to_webdav()

        if verify_etag and exists:
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
        if not self._update_body_cache(uniqueid, content):
            self.body_cache.pop(uniqueid, None)

    def changeProperties(self, uniqueid, properties):
        uniqueid = self._normalize(uniqueid)
        content = self._get_content(uniqueid)
        if content is None:
            raise KeyError(f'The resource {uniqueid} does not exist.')
        if content.lock_status == LockStatus.FOREIGN:
            raise LockedByOtherSystemError(
                uniqueid, f'{uniqueid} is already locked by {content.lock.principal}'
            )
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
                if child.lock and child.lock.status == LockStatus.FOREIGN:
                    raise LockedByOtherSystemError(
                        child.uniqueid,
                        f'Could not delete {child.uniqueid}, because it is locked'
                        f' by {child.lock.principal}',
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
            .where(Content.parent_path.startswith(parent))
            .order_by(Content.parent_path)
            .options(joinedload(Content.lock))
        )
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
        query = select(Content).filter_by(parent_path=parent, name=name)
        if getlock and self.support_locking:
            query = query.options(joinedload(Content.lock))
        return self.session.execute(query).scalars().one_or_none()

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
            (target.parent_path, target.name) = (parent_path, name)
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

        for content in targets:
            self.property_cache[content.uniqueid] = content.to_webdav()
            self._update_body_cache(content.uniqueid, content)
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
            if content.lock.status == LockStatus.FOREIGN:
                raise LockedByOtherSystemError(
                    old_uniqueid, f'{old_uniqueid} is already locked by {content.lock.principal}'
                )
            del content.lock

        sources = [content]
        if content.is_collection:
            sources.extend(self._get_all_children(content.uniqueid))

            for child in sources:
                if child.lock and child.lock.status == LockStatus.FOREIGN:
                    raise LockedByOtherSystemError(
                        old_uniqueid,
                        f'Could not move {child.uniqueid} to {new_uniqueid}, because it is locked'
                        f' by {child.lock.principal}',
                    )

        updates = []
        for content in sources:
            source_uniqueid = content.uniqueid
            target_uniqueid = source_uniqueid.replace(old_uniqueid, new_uniqueid)
            parent, name = self._pathkey(target_uniqueid)
            updates.append({'id': content.id, 'parent_path': parent, 'name': name})

            self.property_cache.pop(source_uniqueid, None)
            self.property_cache[target_uniqueid] = content.to_webdav()
            self.body_cache.pop(source_uniqueid, None)
            self._update_body_cache(target_uniqueid, content)
            if content.is_collection:
                self.child_name_cache.pop(source_uniqueid, None)
                self.child_name_cache[target_uniqueid] = set()
            self._update_parent_child_name_cache(source_uniqueid, 'remove')
            self._update_parent_child_name_cache(target_uniqueid, 'add')
        self.session.execute(update(Content), updates)

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
                    until = pendulum.now('UTC').add(hours=1)
                lock.until = until
                content.lock = lock
                self._update_lock_cache(content.uniqueid, principal, until)
                return lock.token
            case LockStatus.OWN:
                raise LockingError(
                    uniqueid, f'{uniqueid} is already locked' f' by {content.lock.principal}'
                )
            case LockStatus.FOREIGN:
                raise LockedByOtherSystemError(
                    uniqueid, f'{uniqueid} is already locked by {content.lock.principal}'
                )

    def unlock(self, uniqueid):
        uniqueid = self._normalize(uniqueid)
        lock = self._get_content(uniqueid).lock
        if not lock:
            return
        if lock.status == LockStatus.FOREIGN:
            raise LockedByOtherSystemError(
                uniqueid, f'{uniqueid} is already locked by {lock.principal}'
            )
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

    def _search_dav(self, attrlist, expr):
        if (
            len(attrlist) == 1
            and attrlist[0].name == 'uuid'
            and attrlist[0].namespace == DOCUMENT_SCHEMA_NS
        ):
            # Sorely needed performance optimization.
            uuid = expr.operands[-1].replace('urn:uuid:', '')
            content = self.session.execute(select(Content).where(Content.id == uuid)).scalar()
            if content is not None:
                yield (content.uniqueid, '{urn:uuid:%s}' % content.id)
        else:
            query = select(Content).where(self._build_filter(expr))
            result = self.session.execute(query)
            for item in result.scalars():
                data = [item.uniqueid]
                properties = item.to_webdav()
                data.extend([properties[(a.name, a.namespace)] for a in attrlist])
                yield tuple(data)

    search = _search_dav  # BBB

    def search_sql(self, query):
        result = []
        rows = self._execute_suppress_errors(query)
        if rows is None:
            return result

        for content in rows:
            uniqueid = content.uniqueid
            properties = self.property_cache.get(uniqueid)
            if properties is None:
                properties = content.to_webdav()
                self.property_cache[uniqueid] = properties
                self._update_body_cache(content.uniqueid, content)
            resource = self.resource(uniqueid, properties)
            result.append(resource)

        return result

    def search_sql_count(self, query):
        rows = self._execute_suppress_errors(
            query.with_only_columns(
                sqlalchemy.func.count(),
                maintain_column_froms=True,
            )
        )
        if rows is None:
            return 0
        return rows.one()

    def _execute_suppress_errors(self, query, timeout=None):
        try:
            return self.session.execute(
                query, execution_options={'statement_timeout': timeout}
            ).scalars()
        except Exception as e:
            log.warning('Error during search_sql, suppressed', exc_info=True)
            span = opentelemetry.trace.get_current_span()
            span.set_status(Status(StatusCode.ERROR, str(e)))
            self.session.rollback()
            return None

    def _build_filter(self, expr):
        op = expr.operator
        if op == 'and':
            return sqlalchemy.and_(*(self._build_filter(e) for e in expr.operands))
        elif op == 'eq':
            (var, value) = expr.operands
            name = var.name
            namespace = var.namespace.replace(Content.NS, '', 1)
            column = Content.column_by_name(name, namespace, 'read')
            if column is not None:
                return column == value
            value = json.dumps(str(value))  # Apply correct quoting for jsonpath.
            return Content.unsorted.path_match(f'$."{namespace}"."{name}" == {value}')
        else:
            raise RuntimeError(f'Unknown operand {op!r} while building search query')

    def invalidate_cache(self, uniqueid):
        content = self._get_content(uniqueid)
        if content is None:
            self.property_cache.pop(uniqueid, None)
            self.body_cache.pop(uniqueid, None)
            self.child_name_cache.pop(uniqueid, None)
        else:
            self.property_cache[uniqueid] = content.to_webdav()
            if not self._update_body_cache(content.uniqueid, content):
                self.body_cache.pop(uniqueid, None)
            if content.is_collection:
                self._reload_child_name_cache(uniqueid)
        parent = os.path.split(uniqueid)[0]
        self._reload_child_name_cache(parent)


factory = Connector.factory


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
        kw.setdefault('kind', SpanKind.CLIENT)
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
    stmt = delete(Lock).where(Lock.until < pendulum.now('UTC'))
    connector.session.execute(stmt)
    transaction.commit()


@zeit.cms.cli.runner()
def unlock_overdue_locks():
    _unlock_overdue_locks()
