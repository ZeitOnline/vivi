from datetime import datetime
from uuid import uuid4
import collections
import hashlib

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Unicode,
    UnicodeText,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr, mapped_column, relationship
import pytz
import sqlalchemy

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.connector.interfaces import INTERNAL_PROPERTY, DeleteProperty, LockStatus
from zeit.connector.lock import lock_is_foreign
from zeit.connector.types import TIMESTAMP, JSONBTuple
import zeit.connector.interfaces


ID_NAMESPACE = zeit.connector.interfaces.ID_NAMESPACE[:-1]


class Base(sqlalchemy.orm.DeclarativeBase):
    @classmethod
    def Index(cls, *args, name=None, ops=None, **kw):
        if name is not None:
            name = f'ix_{cls.__tablename__}_{name}'
        if ops:
            assert len(args) == 1
            kw['postgresql_ops'] = {args[0]: ops}
            if ops.startswith('json'):
                kw['postgresql_using'] = 'gin'
        return Index(name, *args, **kw)


class CommonMetadata:
    channels = mapped_column(
        JSONBTuple,
        info={'namespace': 'document', 'name': 'channels'},
    )
    access = mapped_column(Unicode, info={'namespace': 'document', 'name': 'access'})
    product = mapped_column(Unicode, info={'namespace': 'workflow', 'name': 'product-id'})
    ressort = mapped_column(Unicode, info={'namespace': 'document', 'name': 'ressort'})
    sub_ressort = mapped_column(Unicode, info={'namespace': 'document', 'name': 'sub_ressort'})
    series = mapped_column(Unicode, info={'namespace': 'document', 'name': 'serie'})

    print_ressort = mapped_column(Unicode, info={'namespace': 'print', 'name': 'ressort'})
    volume_year = mapped_column(Integer, info={'namespace': 'document', 'name': 'year'})
    volume_number = mapped_column(Integer, info={'namespace': 'document', 'name': 'number'})


class Article:
    article_genre = mapped_column(Unicode, info={'namespace': 'document', 'name': 'genre'})


class SemanticChange:
    date_last_modified_semantic = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'last-semantic-change'},
    )


class Modified:
    date_created = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'date_created'},
    )
    date_last_checkout = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'date_last_checkout'},
    )
    date_last_modified = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'date_last_modified'},
    )


class PublishInfo:
    date_first_released = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'date_first_released'},
    )
    date_last_published = mapped_column(
        TIMESTAMP,
        info={'namespace': 'workflow', 'name': 'date_last_published'},
    )
    date_last_published_semantic = mapped_column(
        TIMESTAMP,
        info={'namespace': 'workflow', 'name': 'date_last_published_semantic'},
    )
    date_print_published = mapped_column(
        TIMESTAMP,
        info={'namespace': 'document', 'name': 'print-publish'},
    )
    published = mapped_column(
        Boolean,
        server_default='false',
        nullable=False,
        info={'namespace': 'workflow', 'name': 'published'},
    )


class Content(Base, CommonMetadata, Modified, PublishInfo, SemanticChange, Article):
    __tablename__ = 'properties'

    @declared_attr
    def __table_args__(cls):
        return (
            (
                cls.Index('type'),
                cls.Index('last_updated'),
                cls.Index(
                    'parent_path',
                    ops='varchar_pattern_ops',
                    name='parent_path_pattern',
                ),
                cls.Index(
                    'parent_path',
                    'name',
                    unique=True,
                    name='parent_path_name',
                ),
                cls.Index('unsorted', ops='jsonb_path_ops'),
                cls.Index('channels', ops='jsonb_path_ops'),
            )
            + tuple(
                cls.Index(getattr(cls, column).desc().nulls_last())
                for column in [
                    'date_last_modified_semantic',
                    'date_last_published',
                    'date_last_published_semantic',
                    'date_first_released',
                ]
            )
            + tuple(
                cls.Index(getattr(cls, column))
                for column in [
                    'access',
                    'article_genre',
                    'print_ressort',
                    'product',
                    'published',
                    'ressort',
                    'series',
                    'sub_ressort',
                    'volume_number',
                    'volume_year',
                ]
            )
        )

    id = mapped_column(Uuid(as_uuid=False), primary_key=True)
    type = mapped_column(Unicode, nullable=False, server_default='unknown')
    is_collection = mapped_column(Boolean, nullable=False, server_default='false')

    body = mapped_column(UnicodeText)

    unsorted = mapped_column(JSONB)

    last_updated = mapped_column(
        TIMESTAMP, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now()
    )

    parent_path = mapped_column(Unicode)
    name = mapped_column(Unicode)

    lock = relationship(
        'Lock',
        uselist=False,
        lazy='noload',
        back_populates='content',
        cascade='delete, delete-orphan',  # Propagate `del content.lock` to DB
        passive_deletes=True,  # Disable any heuristics, only ever explicitly delete Locks
    )

    @classmethod
    def column_by_name(cls, name, namespace):
        namespace = namespace.replace(cls.NS, '', 1)
        for column in cls._columns_with_name():
            if namespace == column.info.get('namespace') and name == column.info.get('name'):
                return column

    @classmethod
    def _columns_with_name(cls):
        return [x for x in sqlalchemy.orm.class_mapper(cls).columns if x.info.get('namespace')]

    @property
    def binary_body(self):
        binary_types = zeit.cms.config.get(
            'zeit.connector', 'binary-types', 'image,file,unknown'
        ).split(',')
        return self.type in binary_types

    @property
    def uniqueid(self):
        return f'{ID_NAMESPACE}{self.parent_path}/{self.name}'

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

        if FEATURE_TOGGLES.find('read_metadata_columns'):
            for column in self._columns_with_name():
                namespace, name = column.info['namespace'], column.info['name']
                value = getattr(self, column.name)
                if value is not None:
                    props[(name, self.NS + namespace)] = value

        if self.lock:
            props[('lock_principal', INTERNAL_PROPERTY)] = self.lock.principal
            props[('lock_until', INTERNAL_PROPERTY)] = self.lock.until
        else:
            props[('lock_principal', INTERNAL_PROPERTY)] = None

        return props

    def from_webdav(self, props):
        if not self.id:
            id = props.get(('uuid', self.NS + 'document'))
            if id is None:
                id = str(uuid4())
            else:
                id = id[10:-1]  # strip off `{urn:uuid:}`
            self.id = id

        type = props.get(('type', self.NS + 'meta'))
        if type:
            self.type = type

        if FEATURE_TOGGLES.find('write_metadata_columns') or FEATURE_TOGGLES.find(
            'write_metadata_columns_strict'
        ):
            for column in self._columns_with_name():
                namespace, name = column.info['namespace'], column.info['name']
                value = props.get((name, self.NS + namespace), self)

                if value is self:
                    continue
                if value is DeleteProperty:
                    setattr(self, column.name, None)
                    continue

                converter = zeit.connector.interfaces.IConverter(column)
                # Need to support mixed properties (str/typed) for these cases:
                # - toggle write, but no toggle read: properties read from
                #   connector are still str, properties written by content layer
                #   are already typed
                # - existing workingcopies may still have str properties
                # - existing cache entries may still have str properties
                # Thus, we also need to keep a sufficient grace period after
                # toggle read is enabled before removing the toggles from the code.
                if isinstance(value, str):
                    value = converter.deserialize(value)

                setattr(self, column.name, value)
                if FEATURE_TOGGLES.find('write_metadata_columns_strict'):
                    props.pop((name, self.NS + namespace), None)
                else:
                    props[name, self.NS + namespace] = converter.serialize(value)

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


class Lock(Base):
    __tablename__ = 'locks'

    id = mapped_column(Uuid(as_uuid=False), ForeignKey('properties.id'), primary_key=True)
    principal = mapped_column(Unicode, nullable=False)
    until = mapped_column(TIMESTAMP, nullable=False)

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
