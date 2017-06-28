from zeit.content.video.interfaces import IVideo
import grokcore.component as grok
import zope.interface
import zope.schema


class dictproperty(object):
    """Maps a property from a CMS name to a BC name, and performs type
    conversion, using an associated CMS schema field."""

    # Might be cleaner if we figured this out by ourselves, but that would be
    # mechanically finicky and doesn't seem worth the hassle. So we simply have
    # Video.properties set it for us instead.
    __name__ = None

    def __init__(self, bc_name, iface=None, fieldname=None, field=None):
        """The value is stored in the instance's data dict, under the key
        ``bc_name`` (may contain '/' to denote nested dicts).

        Pass either iface and fieldname, or for special cases a
        zope.schema.Field instance, so we can look up type conversion
        accordingly, and access CMS values that reside in adapters.
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

    def __get__(self, instance, cls):
        if instance is None:
            return self
        data = instance.data
        for x in self.path:
            data = data.get(x, {})
        value = data[self.name]
        converter = ITypeConverter(self.field)
        return converter.to_cms(value)

    def __set__(self, instance, value):
        if self.field.readonly:
            raise AttributeError('Cannot set %s', self.bc_name)
        data = instance.data
        for x in self.path:
            data = data.setdefault(x, {})
        converter = ITypeConverter(self.field)
        data[self.name] = converter.to_bc(value)


class Video(object):
    """Converts video data between CMS and Brightcove.

    * Stores json data received from the Brightcove API in a nested dict
    * Presents it as properties with CMS names and with CMS types for reading
    * On write, those properties convert to BC names and BC types

    Can be constructed from both a CMS object and a BC API result dict.
    """

    id = dictproperty('id', field=zope.schema.TextLine(readonly=True))
    title = dictproperty('name', IVideo, 'title')
    teaserText = dictproperty('description', IVideo, 'teaserText')

    commentsAllowed = dictproperty(
        'custom_fields/allow_comments', IVideo, 'commentsAllowed')
    ressort = dictproperty('custom_fields/ressort', IVideo, 'ressort')

    def __init__(self):
        self.data = {}

    @classmethod
    def from_cms(cls, video):
        instance = cls()
        instance.data['id'] = video.brightcove_id
        adapters = {}
        for prop in instance.properties:
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

    @property
    def properties(self):
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


class ITypeConverter(zope.interface.Interface):

    def to_bc(value):
        pass

    def to_cms(value):
        pass


class DefaultPassthroughConverter(grok.Adapter):

    grok.context(zope.interface.Interface)
    grok.implements(ITypeConverter)

    def to_bc(self, value):
        return value

    def to_cms(self, value):
        return value


class BoolConverter(grok.Adapter):

    grok.context(zope.schema.Bool)
    grok.implements(ITypeConverter)

    def to_bc(self, value):
        return '1' if value else '0'

    def to_cms(self, value):
        return value == '1'
