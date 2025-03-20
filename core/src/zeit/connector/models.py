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
from sqlalchemy import text as sql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr, mapped_column, relationship
import pendulum
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


CREATE_EXTENSION_UNACCENT = 'CREATE EXTENSION IF NOT EXISTS unaccent;'
# Support using the unaccent() function in an index expression, see
# <https://stackoverflow.com/questions/11005036/11007216>.
# The (faster?) "language C" wrapper function does not work on CloudSQL.
CREATE_EXTENSION_UNACCENT += """\
CREATE OR REPLACE FUNCTION iunaccent(text) RETURNS text
LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT
RETURN public.unaccent('public.unaccent', $1);"""


@sqlalchemy.event.listens_for(Base.metadata, 'before_create')
def metadata_create(target, connection, **kw):
    connection.execute(sql(CREATE_EXTENSION_UNACCENT))


class CommonMetadata:
    channels = mapped_column(JSONBTuple, info={'namespace': 'document', 'name': 'channels'})
    access = mapped_column(Unicode, info={'namespace': 'document', 'name': 'access'})
    product = mapped_column(Unicode, info={'namespace': 'workflow', 'name': 'product-id'})
    ressort = mapped_column(Unicode, info={'namespace': 'document', 'name': 'ressort'})
    sub_ressort = mapped_column(Unicode, info={'namespace': 'document', 'name': 'sub_ressort'})
    series = mapped_column(Unicode, info={'namespace': 'document', 'name': 'serie'})

    print_ressort = mapped_column(Unicode, info={'namespace': 'print', 'name': 'ressort'})
    volume_year = mapped_column(Integer, info={'namespace': 'document', 'name': 'year'})
    volume_number = mapped_column(Integer, info={'namespace': 'document', 'name': 'volume'})
    print_page = mapped_column(Integer, info={'namespace': 'document', 'name': 'page'})

    accepted_entitlements = mapped_column(
        Unicode, info={'namespace': 'document', 'name': 'accepted_entitlements'}
    )


class ContentTypes:
    audio_premium_enabled = mapped_column(Boolean, info={'namespace': 'print', 'name': 'has_audio'})
    audio_speech_enabled = mapped_column(
        Boolean, info={'namespace': 'document', 'name': 'audio_speechbert'}
    )

    article_genre = mapped_column(Unicode, info={'namespace': 'document', 'name': 'genre'})
    article_header = mapped_column(Unicode, info={'namespace': 'document', 'name': 'header_layout'})

    author_firstname = mapped_column(Unicode, info={'namespace': 'author', 'name': 'firstname'})
    author_lastname = mapped_column(Unicode, info={'namespace': 'author', 'name': 'lastname'})
    author_displayname = mapped_column(
        Unicode, info={'namespace': 'author', 'name': 'display_name'}
    )
    author_initials = mapped_column(Unicode, info={'namespace': 'author', 'name': 'initials'})
    author_department = mapped_column(Unicode, info={'namespace': 'author', 'name': 'department'})
    author_ssoid = mapped_column(Integer, info={'namespace': 'author', 'name': 'ssoid'})
    author_hdok_id = mapped_column(Integer, info={'namespace': 'author', 'name': 'hdok_id'})
    author_vgwort_id = mapped_column(Integer, info={'namespace': 'author', 'name': 'vgwort_id'})
    author_vgwort_code = mapped_column(Unicode, info={'namespace': 'author', 'name': 'vgwort_code'})

    centerpage_type = mapped_column(Unicode, info={'namespace': 'zeit.content.cp', 'name': 'type'})

    gallery_type = mapped_column(
        Unicode, info={'namespace': 'zeit.content.gallery', 'name': 'type'}
    )
    video_type = mapped_column(Unicode, info={'namespace': 'video', 'name': 'type'})


class Timestamps:
    date_last_modified_semantic = mapped_column(
        TIMESTAMP, info={'namespace': 'document', 'name': 'last-semantic-change'}
    )

    date_created = mapped_column(TIMESTAMP, info={'namespace': 'document', 'name': 'date_created'})
    date_last_checkout = mapped_column(
        TIMESTAMP, info={'namespace': 'document', 'name': 'date_last_checkout'}
    )
    date_last_modified = mapped_column(
        TIMESTAMP, info={'namespace': 'document', 'name': 'date_last_modified'}
    )

    date_first_released = mapped_column(
        TIMESTAMP, info={'namespace': 'document', 'name': 'date_first_released'}
    )
    date_last_published = mapped_column(
        TIMESTAMP, info={'namespace': 'workflow', 'name': 'date_last_published'}
    )
    date_last_published_semantic = mapped_column(
        TIMESTAMP,
        info={
            'namespace': 'workflow',
            'name': 'date_last_published_semantic',
        },
    )
    date_print_published = mapped_column(
        TIMESTAMP, info={'namespace': 'document', 'name': 'print-publish'}
    )
    date_scheduled_publish = mapped_column(
        TIMESTAMP, info={'namespace': 'workflow', 'name': 'released_from', 'migration': 'wcm_694'}
    )
    date_scheduled_retract = mapped_column(
        TIMESTAMP, info={'namespace': 'workflow', 'name': 'released_to', 'migration': 'wcm_694'}
    )


class Miscellaneous:
    seo_meta_robots = mapped_column(
        Unicode, info={'namespace': 'document', 'name': 'html-meta-robots'}
    )


class VGWort:
    vgwort_reported_on = mapped_column(
        TIMESTAMP, info={'namespace': 'vgwort', 'name': 'reported_on', 'migration': 'wcm_758'}
    )
    vgwort_reported_error = mapped_column(
        Unicode, info={'namespace': 'vgwort', 'name': 'reported_error', 'migration': 'wcm_758'}
    )
    vgwort_public_token = mapped_column(
        Unicode, info={'namespace': 'vgwort', 'name': 'public_token', 'migration': 'wcm_758'}
    )
    vgwort_private_token = mapped_column(
        Unicode, info={'namespace': 'vgwort', 'name': 'private_token', 'migration': 'wcm_758'}
    )


class Content(Base, CommonMetadata, ContentTypes, Timestamps, Miscellaneous, VGWort):
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
                cls.Index(
                    sqlalchemy.func.iunaccent(cls.author_lastname),
                    postgresql_where=cls.type == 'author',
                    ops='varchar_pattern_ops',
                    name='author_lastname',
                ),
            )
            + tuple(
                cls.Index(getattr(cls, column).desc().nulls_last())
                for column in [
                    'date_last_modified_semantic',
                    'date_last_published',
                    'date_last_published_semantic',
                    'date_first_released',
                    'date_scheduled_publish',
                    'date_scheduled_retract',
                ]
            )
            + tuple(
                cls.Index(getattr(cls, column))
                for column in [
                    'access',
                    'article_genre',
                    'article_header',
                    'audio_premium_enabled',
                    'author_hdok_id',
                    'author_ssoid',
                    'centerpage_type',
                    'print_ressort',
                    'product',
                    'published',
                    'ressort',
                    'series',
                    'sub_ressort',
                    'video_type',
                    'volume_number',
                    'volume_year',
                    'vgwort_private_token',
                    'vgwort_reported_error',
                    'vgwort_reported_on',
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

    published = mapped_column(
        Boolean,
        server_default='false',
        nullable=False,
        info={'namespace': 'workflow', 'name': 'published'},
    )

    lock = relationship(
        'Lock',
        uselist=False,
        lazy='noload',
        back_populates='content',
        cascade='delete, delete-orphan',  # Propagate `del content.lock` to DB
        passive_deletes=True,  # Disable any heuristics, only ever explicitly delete Locks
    )

    @classmethod
    def column_by_name(cls, name, namespace, mode='always'):
        namespace = namespace.replace(cls.NS, '', 1)
        for column in cls._columns_with_name(mode):
            if namespace == column.info.get('namespace') and name == column.info.get('name'):
                return column

    _COLUMN_MODES = ('always', 'read', 'write', 'strict')

    @classmethod
    def _columns_with_name(cls, mode):
        assert mode in cls._COLUMN_MODES
        result = []
        for column in sqlalchemy.orm.class_mapper(cls).columns:
            if not column.info.get('namespace'):
                continue
            migration = column.info.get('migration')
            if (
                migration is None
                or mode == 'always'
                or FEATURE_TOGGLES.find(f'column_{mode}_{migration}')
            ):
                result.append(column)

        return result

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

        for column in self._columns_with_name('read'):
            namespace, name = column.info['namespace'], column.info['name']
            value = getattr(self, column.name)
            if value is not None:
                converter = zeit.connector.interfaces.IConverter(column)
                props[(name, self.NS + namespace)] = converter.serialize(value)

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

        for column in self._columns_with_name('write'):
            namespace, name = column.info['namespace'], column.info['name']
            value = props.get((name, self.NS + namespace), self)

            if value is self:
                continue
            if value is DeleteProperty:
                setattr(self, column.name, None)
                continue
            if not isinstance(value, str):
                raise ValueError('Expected str, got %r' % value)

            converter = zeit.connector.interfaces.IConverter(column)
            try:
                setattr(self, column.name, converter.deserialize(value))
            except Exception as e:
                converter = converter.__class__.__name__
                raise ValueError(
                    f'Cannot convert {value!r} to {column.name} with {converter}: {e}'
                ) from e

            migration = column.info.get('migration')
            if migration and FEATURE_TOGGLES.find(f'column_strict_{migration}'):
                props.pop((name, self.NS + namespace), None)

        unsorted = collections.defaultdict(dict)
        for (k, ns), v in props.items():
            if v is DeleteProperty:
                continue
            if ns == INTERNAL_PROPERTY:
                continue
            if not isinstance(v, str):
                raise ValueError('Expected str, got %r' % v)

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
        elif self.until < pendulum.now('UTC'):
            return LockStatus.TIMED_OUT
        elif not lock_is_foreign(self.principal):
            return LockStatus.OWN
        else:
            return LockStatus.FOREIGN
