from zeit.content.video.interfaces import IVideo
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
        ``bc_name``. Pass either iface and fieldname, or for special cases a
        zope.schema.Field instance, so we can look up type conversion
        accordingly, and access CMS values that reside in adapters.
        """
        self.bc_name = bc_name

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
        return instance.data[self.bc_name]

    def __set__(self, instance, value):
        if self.field.readonly:
            raise AttributeError('Cannot set %s', self.bc_name)
        instance.data[self.bc_name] = value


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

    def __init__(self):
        self.data = {}

    @classmethod
    def from_cms(cls, video):
        instance = cls()
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
