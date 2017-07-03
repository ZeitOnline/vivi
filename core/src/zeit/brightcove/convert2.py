from zeit.content.video.interfaces import IVideo
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zc.iso8601.parse
import zeit.cms.interfaces
import zope.interface
import zope.schema


class dictproperty(object):
    """Maps a property from a CMS name to a BC name, and performs type
    conversion, using an associated CMS schema field."""

    # Might be cleaner if we figured this out by ourselves, but that would be
    # mechanically finicky and doesn't seem worth the hassle. So we simply have
    # Video.properties set it for us instead.
    __name__ = None

    def __init__(self, bc_name, iface=None, fieldname=None, field=None,
                 converter=None):
        """The value is stored in the instance's data dict, under the key
        ``bc_name`` (may contain '/' to denote nested dicts).

        Pass either iface and fieldname, or for special cases a
        zope.schema.Field instance, so we can look up type conversion
        accordingly, and access CMS values that reside in adapters.

        You can pass the class name of an ITypeConverter (to prevent source
        code ordering / import time issues), otherwise one will be looked up
        for the given field.
        """
        self.bc_name = bc_name
        segments = self.bc_name.split('/')
        self.path = segments[:-1]
        self.name = segments[-1]

        assert (iface and fieldname) or field
        if field:
            self.iface = None
            self.field = field
        else:
            self.iface = iface
            self.field = iface[fieldname]

        self._converter = converter

    def __get__(self, instance, cls):
        if instance is None:
            return self
        data = instance.data
        for x in self.path:
            data = data.get(x, {})
        try:
            value = data[self.name]
        except KeyError:
            return self.field.default
        return self.converter.to_cms(value)

    def __set__(self, instance, value):
        if self.field.readonly:
            raise AttributeError('Cannot set %s', self.bc_name)
        data = instance.data
        for x in self.path:
            data = data.setdefault(x, {})
        data[self.name] = self.converter.to_bc(value)

    @cachedproperty
    def converter(self):
        if self._converter is None:
            return ITypeConverter(self.field)
        else:
            return globals()[self._converter](self.field)


class ProductProperty(dictproperty):

    def __get__(self, instance, cls):
        if instance is None:
            return self
        if (not instance.data.get('custom_fields', {}).get('produkt-id') and
                instance.data.get('reference_id')):
            return zeit.cms.content.sources.PRODUCT_SOURCE(None).find(
                'Reuters')  # XXX Magic hard-coded defaults.
        return super(ProductProperty, self).__get__(instance, cls)


class RelatedProperty(dictproperty):

    RELATED_COUNT = range(1, 6)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        custom = instance.data.get('custom_fields', {})
        if not custom:
            return self.field.default
        return self.converter.to_cms(
            [custom.get('ref_link%s' % i) for i in self.RELATED_COUNT])

    def __set__(self, instance, value):
        if not value:
            value = ()
        custom = instance.data.setdefault('custom_fields', {})
        for i in self.RELATED_COUNT:
            try:
                item = value[i - 1]
            except IndexError:
                custom['ref_link%s' % i] = ''
                custom['ref_title%s' % i] = ''
            else:
                id, title = self.converter.to_bc(item)
                custom['ref_link%s' % i] = id
                custom['ref_title%s' % i] = title


class Video(object):
    """Converts video data between CMS and Brightcove.

    * Stores json data received from the Brightcove API in a nested dict
    * Presents it as properties with CMS names and with CMS types for reading
    * On write, those properties convert to BC names and BC types

    Can be constructed from both a CMS object and a BC API result dict.
    """

    id = dictproperty('id', field=zope.schema.TextLine(readonly=True))

    # read/write fields
    title = dictproperty('name', IVideo, 'title')
    teaserText = dictproperty('description', IVideo, 'teaserText')

    authorships = dictproperty('custom_fields/authors', IVideo, 'authorships',
                               converter='AuthorshipsConverter')
    commentsAllowed = dictproperty(
        'custom_fields/allow_comments', IVideo, 'commentsAllowed')
    commentsPremoderate = dictproperty(
        'custom_fields/premoderate_comments', IVideo, 'commentsPremoderate')
    banner = dictproperty('custom_fields/banner', IVideo, 'banner')
    banner_id = dictproperty('custom_fields/banner-id', IVideo, 'banner_id')
    dailyNewsletter = dictproperty(
        'custom_fields/newsletter', IVideo, 'dailyNewsletter')
    has_recensions = dictproperty(
        'custom_fields/recensions', IVideo, 'has_recensions')
    keywords = dictproperty('custom_fields/cmskeywords', IVideo, 'keywords',
                            converter='KeywordsConverter')
    product = ProductProperty('custom_fields/produkt-id', IVideo, 'product',
                              converter='ProductConverter')
    related = RelatedProperty(
        'custom_fields/ref_*',
        zeit.cms.related.interfaces.IRelatedContent, 'related',
        converter='RelatedConverter')
    ressort = dictproperty('custom_fields/ressort', IVideo, 'ressort')
    serie = dictproperty('custom_fields/serie', IVideo, 'serie',
                         converter='SeriesConverter')
    subtitle = dictproperty('long_description', IVideo, 'subtitle')
    supertitle = dictproperty('custom_fields/supertitle', IVideo, 'supertitle')
    video_still_copyright = dictproperty(
        'custom_fields/credit', IVideo, 'video_still_copyright')

    # readonly fields
    date_created = dictproperty(
        'created_at', field=zope.schema.Datetime(readonly=True))
    date_first_released = dictproperty(
        'published_at',
        zeit.cms.workflow.interfaces.IPublishInfo, 'date_first_released')
    date_last_modified = dictproperty(
        'updated_at',
        zeit.cms.workflow.interfaces.IModified, 'date_last_modified')
    expires = dictproperty(
        'schedule/ends_at', zeit.brightcove.interfaces.IVideo, 'expires')
    ignore_for_update = dictproperty(
        'custom_fields/ignore_for_update',
        field=zope.schema.Bool(readonly=True))
    sources = dictproperty('sources', IVideo, 'renditions',
                           converter='SourceConverter')
    state = dictproperty(
        'state', zeit.brightcove.interfaces.IBrightcoveContent, 'item_state')
    thumbnail = dictproperty('images/thumbnail/src', IVideo, 'thumbnail')
    video_still = dictproperty('images/poster/src', IVideo, 'video_still')

    def __init__(self):
        self.data = {}

    @classmethod
    def find_by_id(cls, id):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        data = api.get_video(id)
        data['sources'] = api.get_video_sources(id)
        return cls.from_bc(data)

    @classmethod
    def from_cms(cls, video):
        instance = cls()
        instance.data['id'] = video.brightcove_id
        adapters = {}
        for prop in instance._dictproperties:
            if prop.field.readonly:
                continue
            wrapped = video
            if prop.iface:
                wrapped = adapters.get(prop.iface)
                if wrapped is None:
                    wrapped = prop.iface(video)
                    adapters[prop.iface] = wrapped
            setattr(instance, prop.__name__, prop.field.get(wrapped))
        return instance

    @classmethod
    def from_bc(cls, data):
        instance = cls()
        instance.data.update(data)
        return instance

    @cachedproperty
    def __parent__(self):
        return zeit.cms.content.interfaces.IAddLocation(self)

    @cachedproperty
    def uniqueId(self):
        path = self.__parent__.uniqueId
        # XXX Folders in mock connector have no trailing slash, but in the real
        # connector they do.
        if not path.endswith('/'):
            path += '/'
        return path + self.id

    @property
    def write_data(self):
        """Copy of our data dict, with all readonly properties removed."""
        data = self.data.copy()  # first-level copy is sufficient right now.
        for prop in self._dictproperties:
            if prop.field.readonly:
                data.pop(prop.bc_name, None)
        return data

    @property
    def _dictproperties(self):
        cls = type(self)
        result = []
        for propname in dir(cls):
            prop = getattr(cls, propname)
            if not isinstance(prop, dictproperty):
                continue
            prop.__name__ = propname
            result.append(prop)
        return result

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.id or '(unknown)')


def update_brightcove(context, event):
    if not event.publishing:
        session = zeit.brightcove.session.get()
        session.update_video(Video.from_cms(context))


def publish_on_checkin(context, event):
    # prevent infinite loop, since there is a checkout/checkin cycle during
    # publishing (to update XML references etc.)
    if not event.publishing:
        zeit.cms.workflow.interfaces.IPublish(context).publish()


@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
@grok.adapter(Video)
def video_location(bcobj):
    conf = zope.app.appsetup.product.getProductConfiguration('zeit.brightcove')
    path = conf['video-folder']
    return zeit.cms.content.add.find_or_create_folder(
        *(path.split('/') + [bcobj.date_created.strftime('%Y-%m')]))


class ITypeConverter(zope.interface.Interface):

    def to_bc(value):
        pass

    def to_cms(value):
        pass


class Converter(grok.Adapter):

    grok.baseclass()
    grok.implements(ITypeConverter)

    def to_bc(self, value):
        return value

    def to_cms(self, value):
        return value


class DefaultPassthroughConverter(Converter):

    grok.context(zope.interface.Interface)


class TextConverter(Converter):

    grok.context(zope.schema.TextLine)

    def to_cms(self, value):
        return unicode(value)


class BoolConverter(Converter):

    grok.context(zope.schema.Bool)

    def to_bc(self, value):
        return '1' if value else '0'

    def to_cms(self, value):
        return value == '1'


class DatetimeConverter(Converter):

    grok.context(zope.schema.Datetime)

    def to_bc(self, value):
        if not value:
            return None
        return value.isoformat()

    def to_cms(self, value):
        if not value:
            return None
        return zc.iso8601.parse.datetimetz(value)


class AuthorshipsConverter(Converter):

    # used explicitly, since we cannot register an adapter for a field instance
    grok.baseclass()

    SEPARATOR = u' '

    def to_bc(self, value):
        return self.SEPARATOR.join(x.target.uniqueId for x in value)

    def to_cms(self, value):
        if not value:
            return self.context.default
        authors = [zeit.cms.interfaces.ICMSContent(x, None)
                   for x in value.split(self.SEPARATOR)]
        return tuple([x for x in authors if x is not None])


class KeywordsConverter(Converter):

    grok.baseclass()

    SEPARATOR = u';'

    def to_bc(self, value):
        return self.SEPARATOR.join(x.code for x in value)

    def to_cms(self, value):
        if not value:
            return self.context.default
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        keywords = [whitelist.get(code)
                    for code in value.split(self.SEPARATOR)]
        return tuple([x for x in keywords if x is not None])


class ProductConverter(Converter):

    grok.baseclass()

    def to_bc(self, value):
        return value.id if value else None

    def to_cms(self, value):
        return self.context.source(None).find(value)


class SeriesConverter(Converter):

    grok.baseclass()

    def to_bc(self, value):
        return value.serienname if value else None

    def to_cms(self, value):
        return self.context.source(None).find(value)


class RelatedConverter(Converter):

    grok.baseclass()

    # Our method signatures are not symmetrical (single- vs multi-valued),
    # but this way it's rather convenient to use in RelatedProperty.

    def to_bc(self, value):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(value, None)
        if metadata and metadata.teaserTitle:
            title = metadata.teaserTitle
        else:
            title = u'unknown'
        return value.uniqueId, title

    def to_cms(self, value):
        result = []
        for item in value:
            if not item:
                continue  # Micro-optimization
            result.append(zeit.cms.interfaces.ICMSContent(item, None))
        return tuple(result)


class SourceConverter(Converter):

    grok.baseclass()

    def to_cms(self, value):
        result = []
        for item in value:
            vr = zeit.content.video.video.VideoRendition()
            vr.url = item.get('src')
            if not vr.url:
                continue
            vr.frame_width = item.get('width')
            vr.video_duration = item.get('duration')
            result.append(vr)
        return tuple(result)
