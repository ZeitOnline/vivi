from zeit.content.video.interfaces import IVideo
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import pendulum
import zeit.brightcove.resolve
import zeit.cms.content.field
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zeit.content.video.video
import zope.component


class Converter(object):

    def __init__(self):
        self.data = {}

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
        return self.__parent__.uniqueId + self.id

    @cachedproperty
    def id(self):
        return str(self.data.get('id', ''))

    @cachedproperty
    def date_created(self):
        return self.cms_date(self.data.get('created_at'))

    @staticmethod
    def bc_bool(value):
        return '1' if value else '0'

    @staticmethod
    def cms_bool(value):
        return value == '1'

    @staticmethod
    def cms_date(value):
        if not value:
            return None
        return pendulum.parse(value)

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.id or '(unknown)')


class Video(Converter):

    @classmethod
    def find_by_id(cls, id):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        data = api.get_video(id)
        if data is not None:
            data['sources'] = api.get_video_sources(id)
        else:
            # Since BC gives us no further information, we need to try and
            # resolve the CMS uniqueId by ourselves.
            cmsobj = zeit.cms.interfaces.ICMSContent(
                zeit.brightcove.resolve.query_video_id(id), None)
            return DeletedVideo(id, cmsobj)
        return cls.from_bc(data)

    @classmethod
    def find_last_modified(cls, hours):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        result = []
        for data in api.find_videos('updated_at:-%sh' % hours):
            data['sources'] = api.get_video_sources(data['id'])
            result.append(cls.from_bc(data))
        return result

    @classmethod
    def from_cms(cls, cmsobj):
        instance = cls()
        data = instance.data
        data['custom_fields'] = custom = {}

        # This is coupled to our IAddLocation and importing implementation.
        data['id'] = cmsobj.__name__

        data['name'] = cmsobj.title
        data['description'] = cmsobj.teaserText
        data['long_description'] = cmsobj.subtitle
        data['economics'] = (
            'AD_SUPPORTED' if cmsobj.has_advertisement else 'FREE')

        custom['authors'] = ' '.join(
            x.target.uniqueId for x in cmsobj.authorships)
        custom['allow_comments'] = cls.bc_bool(cmsobj.commentsAllowed)
        custom['premoderate_comments'] = cls.bc_bool(
            cmsobj.commentsPremoderate)
        custom['banner'] = cls.bc_bool(cmsobj.banner)
        custom['banner_id'] = cmsobj.banner_id
        custom['recensions'] = cls.bc_bool(cmsobj.has_recensions)
        custom['produkt-id'] = cmsobj.product.id if cmsobj.product else None
        custom['cmskeywords'] = u';'.join(x.code for x in cmsobj.keywords)
        custom['ressort'] = cmsobj.ressort
        custom['serie'] = cmsobj.serie.serienname if cmsobj.serie else None
        custom['channels'] = u';'.join([' '.join([x for x in channel if x])
                                        for channel in cmsobj.channels])
        custom['supertitle'] = cmsobj.supertitle
        custom['credit'] = cmsobj.video_still_copyright
        custom['type'] = cmsobj.type

        related = zeit.cms.related.interfaces.IRelatedContent(cmsobj).related
        for i in range(1, 6):
            try:
                item = related[i - 1]
            except IndexError:
                custom['ref_link%s' % i] = ''
                custom['ref_title%s' % i] = ''
            else:
                metadata = zeit.cms.content.interfaces.ICommonMetadata(
                    item, None)
                if metadata and metadata.teaserTitle:
                    title = metadata.teaserTitle
                else:
                    title = u'unknown'
                custom['ref_link%s' % i] = item.uniqueId
                custom['ref_title%s' % i] = title

        # Only strings are allowed in `custom_fields`
        empty = []
        for key, value in custom.items():
            if value is None:
                empty.append(key)
        for key in empty:
            del custom[key]

        return instance

    def apply_to_cms(self, cmsobj):
        data = self.data
        custom = data.get('custom_fields', {})

        zeit.cms.content.field.apply_default_values(
            cmsobj, zeit.content.video.interfaces.IVideo)
        cmsobj.external_id = data.get('id')
        cmsobj.title = data.get('name')
        cmsobj.teaserText = data.get('description')
        cmsobj.subtitle = data.get('long_description')
        authors = [zeit.cms.interfaces.ICMSContent(x, None)
                   for x in custom.get('authors', '').split(' ')]
        cmsobj.authorships = tuple([x for x in authors if x is not None])
        cmsobj.commentsAllowed = self._default_if_missing(
            custom, 'allow_comments', IVideo['commentsAllowed'], self.cms_bool)
        cmsobj.commentsPremoderate = self._default_if_missing(
            custom, 'premoderate_comments', IVideo['commentsPremoderate'],
            self.cms_bool)
        cmsobj.banner = self._default_if_missing(
            custom, 'banner', IVideo['banner'], self.cms_bool)
        cmsobj.banner_id = custom.get('banner_id')
        cmsobj.expires = self.cms_date(
            (data.get('schedule') or {}).get('ends_at'))
        cmsobj.has_recensions = self._default_if_missing(
            custom, 'recensions', IVideo['has_recensions'], self.cms_bool)
        cmsobj.has_advertisement = data.get('economics') == 'AD_SUPPORTED'
        cmsobj.ressort = custom.get('ressort')
        cmsobj.serie = IVideo['serie'].source(None).find(custom.get('serie'))
        cmsobj.supertitle = custom.get('supertitle')
        cmsobj.video_still_copyright = custom.get('credit')
        cmsobj.type = custom.get('type')

        product_source = IVideo['product'].source(cmsobj)
        if not custom.get('produkt-id') and data.get('reference_id'):
            # XXX Magic hard-coded defaults.
            cmsobj.product = product_source.find('Reuters')
        else:
            cmsobj.product = product_source.find(custom.get('produkt-id'))

        channel_source = zeit.cms.content.sources.ChannelSource()(cmsobj)
        subchannel_source = zeit.cms.content.sources.SubChannelSource()(cmsobj)
        channels = []
        for item in custom.get('channels', '').split(';'):
            parts = item.split(' ')
            if len(parts) == 1:
                channel = parts[0]
                subchannel = None
            elif len(parts) == 2:
                channel = parts[0]
                subchannel = parts[1]
            else:
                continue
            if channel in channel_source:
                if subchannel in subchannel_source:
                    channels.append((channel, subchannel))
                else:
                    channels.append((channel, None))
        cmsobj.channels = channels

        related = []
        for item in [custom.get('ref_link%s' % i) for i in range(1, 6)]:
            if not item:
                continue  # Micro-optimization
            related.append(zeit.cms.interfaces.ICMSContent(item, None))
        zeit.cms.related.interfaces.IRelatedContent(
            cmsobj).related = tuple(related)

        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        keywords = [
            whitelist.get(code)
            for code in custom.get('cmskeywords', '').split(';')]
        cmsobj.keywords = tuple([x for x in keywords if x is not None])

        publish = zeit.cms.workflow.interfaces.IPublishInfo(cmsobj)
        publish.date_first_released = self.cms_date(data.get('published_at'))

        if cmsobj.expires and cmsobj.expires > pendulum.now():
            fake_id = cmsobj.uniqueId is None
            if fake_id:
                # Pacify IObjectLog, which is triggered by ITimeBasedPublishing
                cmsobj.uniqueId = self.uniqueId
            try:
                publish.release_period = (None, cmsobj.expires)
            finally:
                if fake_id:
                    cmsobj.uniqueId = None

        zeit.cms.content.interfaces.ISemanticChange(
            cmsobj).last_semantic_change = self.cms_date(
                data.get('updated_at'))

    def _default_if_missing(self, data, key, field, convert=None):
        if key not in data:
            return field.default
        value = data[key]
        if convert is not None:
            value = convert(value)
        return value

    @property
    def write_data(self):
        data = {}
        for key in [
                'custom_fields', 'name', 'description', 'long_description']:
            if key in self.data:
                data[key] = self.data[key]
        return data

    @property
    def state(self):
        return self.data.get('state')

    @property
    def skip_import(self):
        return self.cms_bool(self.data.get('custom_fields', {}).get(
            'ignore_for_update'))


class DeletedVideo(Video):

    def __init__(self, id, cmsobj):
        # We fake just enough API so VideoUpdater can perform the delete
        # (or skip us entirely if we don't even have a CMS object anymore).
        super(DeletedVideo, self).__init__()
        self.data['id'] = id
        if cmsobj is not None:
            self.__dict__['__parent__'] = cmsobj.__parent__
            self.__dict__['uniqueId'] = cmsobj.uniqueId
        else:
            self.__dict__['__parent__'] = None
            self.__dict__['uniqueId'] = (
                'http://xml.zeit.de/__deleted_video__/' + id)


@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
@grok.adapter(Video)
def video_location(bcobj):
    conf = zope.app.appsetup.product.getProductConfiguration('zeit.brightcove')
    path = conf['video-folder']
    return zeit.cms.content.add.find_or_create_folder(
        *(path.split('/') + [bcobj.date_created.strftime('%Y-%m')]))


class Playlist(Converter):

    @classmethod
    def find_by_id(cls, id):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        data = api.get_playlist(id)
        if data is None:
            return None
        return cls.from_bc(data)

    @classmethod
    def find_all(cls):
        api = zope.component.getUtility(zeit.brightcove.interfaces.ICMSAPI)
        result = []
        for data in api.get_all_playlists():
            result.append(cls.from_bc(data))
        return result

    def apply_to_cms(self, cmsobj):
        cmsobj.title = self.data.get('name')
        cmsobj.teaserText = self.data.get('description')

        zeit.cms.content.interfaces.ISemanticChange(
            cmsobj).last_semantic_change = self.cms_date(
                self.data.get('updated_at'))

        videos = []
        for id in self.data.get('video_ids', ()):
            resolved = zeit.brightcove.resolve.query_video_id(id)
            if resolved:
                # This is really wasteful and only due to XMLReferenceUpdater.
                content = zeit.cms.interfaces.ICMSContent(resolved, None)
                if content is not None:
                    videos.append(content)
        cmsobj.videos = videos

    @property
    def updated_at(self):
        return self.cms_date(self.data.get('updated_at'))


@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
@grok.adapter(Playlist)
def playlist_location(bcobj):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.brightcove')
    path = config['playlist-folder']
    return zeit.cms.content.add.find_or_create_folder(*path.split('/'))
