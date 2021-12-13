from gocept.cache.property import TransactionBoundCache
from io import BytesIO
from sqlalchemy import Column, Unicode
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSONB
from urllib.parse import urlparse
from uuid import uuid4
from zeit.connector.resource import CachedResource
import collections
import sqlalchemy
import sqlalchemy.orm
import transaction
import zeit.connector.interfaces
import zope.interface
import zope.sqlalchemy


@zope.interface.implementer(zeit.connector.interfaces.IConnector)
class Connector:

    def __init__(self, dsn, body_path):
        self.body_path = body_path.rstrip('/')

        self.dsn = dsn
        self.engine = sqlalchemy.create_engine(dsn, future=True)
        self.session = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine, future=True))
        zope.sqlalchemy.register(self.session)
        sqlalchemy.event.listen(self.session, 'after_attach', cache_object)
        METADATA.create_all(self.engine)

    @classmethod
    @zope.interface.implementer(zeit.connector.interfaces.IConnector)
    def factory(cls):
        import zope.app.appsetup.product
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.connector') or {}
        return cls(config['dsn'], config['repository-path'])

    def __getitem__(self, id):
        props = self._get_properties(id)
        if props is None:
            raise KeyError(id)
        return CachedResource(
            id, id.rstrip('/').split('/')[-1], props.type,
            props.to_dict, lambda: self._get_body(props.body),
            'resource-type-is-irrelevant')

    id_cache = TransactionBoundCache('_v_id_cache', dict)

    def _get_properties(self, uniqueid):
        uniqueid = uniqueid.rstrip('/')
        props = self.id_cache.get(uniqueid)
        if props is None:
            path = urlparse(uniqueid).path
            props = self.session.execute(
                select(Properties).filter_by(url=path)).scalars().first()
            self.id_cache[uniqueid] = props
        return props

    body_cache = TransactionBoundCache('_v_body_cache', dict)

    # XXX filesystem to be replaced by GCS
    def _get_body(self, path):
        data = self.body_cache.get(path)
        if data is None:
            fspath = self.body_path + path
            try:
                with open(fspath, 'rb') as f:
                    data = f.read()
            except Exception:
                data = b''
            self.body_cache[path] = data
        return BytesIO(data)

    def __contains__(self, id):
        try:
            self[id]
            return True
        except KeyError:
            return False

    def __setitem__(self, id, resource):
        resource.id = id
        self.add(resource)

    def add(self, resource, verify_etag=True):
        uniqueid = resource.id.rstrip('/')
        props = self._get_properties(uniqueid)
        exists = props is not None
        if not exists:
            props = Properties()
        props.from_dict(resource.properties)
        props.url = urlparse(uniqueid).path
        if not exists:
            self.session().add(props)

    def listCollection(self, id):
        import traceback
        traceback.print_stack()
        return ()


factory = Connector.factory  # zope.dottedname does not support classmethods


def cache_object(session, instance):
    # Prevent garbage collection,
    # taken from https://github.com/sqlalchemy/sqlalchemy/discussions/7246
    cache = session.info.get('strong_set')
    if cache is None:
        session.info['strong_set'] = cache = set()
    cache.add(instance)


@sqlalchemy.event.listens_for(sqlalchemy.orm.Mapper, 'load')
def object_loaded(instance, ctx):
    cache_object(ctx.session, instance)


class PassthroughConnector(Connector):

    def __init__(self, dsn, body_path):
        super().__init__(dsn, body_path)
        self.fs = zeit.connector.filesystem.Connector(body_path)

    def listCollection(self, id):
        return super().listCollection(id) or self.fs.listCollection(id)

    def __getitem__(self, id):
        try:
            return super().__getitem__(id)
        except KeyError:
            res = self.fs[id]
            if res.properties[('type', NS + 'meta')] != 'folder':
                self[id] = res
                transaction.commit()
            return res


passthrough_factory = PassthroughConnector.factory


METADATA = sqlalchemy.MetaData()
DBObject = sqlalchemy.orm.declarative_base(metadata=METADATA)
NS = 'http://namespaces.zeit.de/CMS/'


class Properties(DBObject):

    __tablename__ = 'properties'

    id = Column(Unicode, primary_key=True)
    url = Column(Unicode, unique=True, nullable=False)
    type = Column(Unicode, nullable=False, server_default='unknown')

    unsorted = Column(JSONB)

    @property
    def body(self):
        return self.url  # XXX GCS will use self.id

    def to_dict(self):
        props = {}
        for ns, d in self.unsorted.items():
            for k, v in d.items():
                props[(k, ns)] = v
        return props

    def from_dict(self, props):
        id = props.get(('uuid', NS + 'document'))
        if id is None:
            id = str(uuid4())
        self.id = id

        # XXX implement a general mapping
        self.type = props.get(('type', NS + 'meta'))

        unsorted = collections.defaultdict(dict)
        for (k, ns), v in props.items():
            unsorted[ns][k] = v
        self.unsorted = unsorted
