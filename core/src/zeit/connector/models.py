from datetime import datetime
from uuid import uuid4
import collections
import hashlib

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Index,
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
import zeit.connector.interfaces


ID_NAMESPACE = zeit.connector.interfaces.ID_NAMESPACE[:-1]


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class CommonMetadata:
    @staticmethod
    def table_args(tablename):
        return (Index(f'ix_{tablename}_channels', 'channels', postgresql_using='gin'),)

    # converter, use name to lookup IConverter instead of type
    channels = mapped_column(
        JSONB,
        nullable=True,
        info={'namespace': 'document', 'name': 'channels'},
    )


class SemanticChange:
    date_last_modified_semantic = mapped_column(
        TIMESTAMP(timezone=True),
        info={'namespace': 'document', 'name': 'last-semantic-change'},
    )


class Modified:
    date_created = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'document', 'name': 'date_created'},
    )
    date_last_checkout = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'document', 'name': 'date_last_checkout'},
    )


class PublishInfo:
    date_first_released = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'document', 'name': 'date_first_released'},
    )
    date_last_published = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'workflow', 'name': 'date_last_published'},
    )
    date_last_published_semantic = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'workflow', 'name': 'date_last_published_semantic'},
    )
    date_print_published = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        info={'namespace': 'document', 'name': 'print-publish'},
    )


class DevelopmentCommonMetadata:
    access = mapped_column(Unicode, index=True, info={'namespace': 'document', 'name': 'access'})


class ContentBase:
    __abstract__ = True
    __tablename__ = 'properties'

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index(
                f'ix_{cls.__tablename__}_parent_path_pattern',
                'parent_path',
                postgresql_ops={'parent_path': 'varchar_pattern_ops'},
            ),
            Index(f'ix_{cls.__tablename__}_parent_path_name', 'parent_path', 'name', unique=True),
            Index(
                f'ix_{cls.__tablename__}_unsorted',
                'unsorted',
                postgresql_using='gin',
                postgresql_ops={'unsorted': 'jsonb_path_ops'},
            ),
        )

    id = mapped_column(Uuid(as_uuid=False), primary_key=True)
    type = mapped_column(Unicode, nullable=False, server_default='unknown', index=True)
    is_collection = mapped_column(Boolean, nullable=False, server_default='false')

    body = mapped_column(UnicodeText)

    unsorted = mapped_column(JSONB)

    last_updated = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        index=True,
    )

    parent_path = mapped_column(Unicode)
    name = mapped_column(Unicode)

    lock_class = NotImplemented

    @declared_attr
    def lock(cls):
        return relationship(
            cls.lock_class,
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
                props[(name, self.NS + namespace)] = getattr(self, column.name)

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

        if FEATURE_TOGGLES.find('write_metadata_columns'):
            for column in self._columns_with_name():
                namespace, name = column.info['namespace'], column.info['name']
                value = props.get((name, self.NS + namespace), self)
                if value is not self:
                    setattr(self, column.name, value)
                    props.pop((name, self.NS + namespace), None)

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


class LockBase:
    __abstract__ = True
    __tablename__ = 'locks'

    id = mapped_column(Uuid(as_uuid=False), ForeignKey('properties.id'), primary_key=True)
    principal = mapped_column(Unicode, nullable=False)
    until = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    content_class = NotImplemented

    @declared_attr
    def content(cls):
        return relationship(cls.content_class, uselist=False, lazy='noload', back_populates='lock')

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


class Content(Base, ContentBase, CommonMetadata, Modified, PublishInfo, SemanticChange):
    lock_class = 'Lock'

    @declared_attr.directive
    def __table_args__(cls):
        """every new inheritance level needs to re-apply the table_args"""
        return super().__table_args__ + CommonMetadata.table_args(cls.__tablename__)


class Lock(Base, LockBase):
    content_class = 'Content'


class DevelopmentBase(sqlalchemy.orm.DeclarativeBase):
    """Experimental development features, not ready for any deployment or migration!"""


class DevelopmentContent(
    DevelopmentBase,
    ContentBase,
    CommonMetadata,
    Modified,
    PublishInfo,
    SemanticChange,
    DevelopmentCommonMetadata,
):
    lock_class = 'LockWithMetadataColumns'


# Having to duplicate all classes (and add indirections to their `relationship()`s)
# is annoying, but there's no obvious way around it.
class LockWithMetadataColumns(DevelopmentBase, LockBase):
    content_class = 'DevelopmentContent'
