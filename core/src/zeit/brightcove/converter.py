# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import transaction
import zeit.brightcove.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zeit.cms.type
import zeit.content.video.interfaces
import zeit.content.video.playlist
import zeit.content.video.video
import zope.component
import zope.interface


class mapped(object):

    field = None

    def __init__(self, *path):
        assert path
        self.path = path

    def __get__(self, instance, class_):
        if instance is None:
            return self
        try:
            return self._get_from_dict(instance.data)
        except KeyError:
            if self.field is None:
                self._guess_field(class_)
            if self.field is not None:
                return self.field.default

    def _guess_field(self, class_):
        for key, value in class_.__dict__.items():
            if value is self:
                break
        else:
            return
        for interface in zope.interface.implementedBy(class_):
            try:
                field = interface[key]
            except KeyError:
                pass
            else:
                self.field = field
                break

    def _get_from_dict(self, value):
        for key in self.path:
            value = value[key]
        return value

    def __set__(self, instance, value):
        data = instance.data
        for key in self.path[:-1]:
            data = data.setdefault(key, {})
        data[self.path[-1]] = value
        instance.save_to_brightcove()


class mapped_bool(mapped):

    def _get_from_dict(self, value):
        value = super(mapped_bool, self)._get_from_dict(value)
        return value == '1'

    def __set__(self, instance, value):
        value = '1' if value else '0'
        super(mapped_bool, self).__set__(instance, value)


class mapped_keywords(mapped):
    """Maps the labels stored in brightcove to a list of tags.
    """

    def __get__(self, instance, class_):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        value = super(mapped_keywords, self).__get__(instance, class_)
        result = []
        if value:
            for code in value.split(';'):
                tag = whitelist.get(code)
                if tag is not None:
                    result.append(tag)
        return tuple(result)

    def __set__(self, instance, value):
        value = ';'.join(tag.code for tag in value)
        super(mapped_keywords, self).__set__(instance, value)


class mapped_datetime(mapped):

    def __get__(self, instance, class_):
        value = super(mapped_datetime, self).__get__(instance, class_)
        if not value:
            return None
        date = datetime.datetime.utcfromtimestamp(int(value)/1000)
        return pytz.utc.localize(date)

    def __set__(self, instance, value):
        value = str(int(value.strftime('%s')) * 1000)
        super(mapped_datetime, self).__set__(instance, value)


class mapped_product(mapped):

    def _get_from_dict(self, value):
        if (value['customFields']['produkt-id'] is None and
            value['referenceId'] is not None):
            return 'Reuters'
        for key in self.path:
            value = value[key]
        return value


class BCContent(object):
    # XXX remove at some point

    pass


class Converter(object):

    zope.interface.implements(zeit.brightcove.interfaces.IBrightcoveContent)

    data = None
    id = mapped('id')
    title = mapped('name')
    teaserText = mapped('shortDescription')
    brightcove_thumbnail = mapped('thumbnailURL')

    def __init__(self, data, connection=None):
        if data is not None:
            self.data = data
            if 'customFields' in self.data:
                self.data['customFields'] = self.data['customFields']
            self.__name__ = '%s-%s' % (self.type, self.data['id'])
            self.uniqueId = 'http://xml.zeit.de/brightcove-folder/%s' % (
                self.__name__)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.__name__ == other.__name__

    @property
    def thumbnail(self):
        return self.data['thumbnailURL']

    @classmethod
    def find_by_id(cls, id):
        return iter(cls.find_by_ids([id])).next()

    @staticmethod
    def get_connection():
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IAPIConnection)

    def save_to_brightcove(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(self):
            return
        registered = getattr(self, '_v_save_hook_registered', False)
        if not registered:
            transaction.get().addBeforeCommitHook(self._save)
            self._v_save_hook_registered = True

    def _save(self):
        try:
            del self._v_save_hook_registered
        except AttributeError:
            pass
        __traceback_info__ = (self.data,)

        data = dict(self.data)
        if 'customFields' in data:
            data['customFields'] = dict(data['customFields'])
        READ_ONLY = ['lastModifiedDate', 'creationDate', 'publishedDate']
        for field in READ_ONLY:
            data.pop(field, None)
        self.get_connection().post('update_video', video=data)


class Video(Converter):

    zope.interface.implements(zeit.brightcove.interfaces.IVideo)

    type = 'video'
    id_prefix = 'vid' # for old-style asset IDs
    commentsAllowed = mapped_bool('customFields', 'allow_comments')
    banner = mapped_bool('customFields', 'banner')
    banner_id = mapped('customFields', 'banner-id')
    breaking_news = mapped_bool('customFields', 'breaking-news')
    dailyNewsletter = mapped_bool('customFields', 'newsletter')
    has_recensions = mapped_bool('customFields', 'recensions')
    item_state = mapped('itemState')
    keywords = mapped_keywords('customFields', 'cmskeywords')
    product_id = mapped('customFields', 'produkt-id')
    ressort = mapped('customFields', 'ressort')
    serie = mapped('customFields', 'serie')
    subtitle = mapped('longDescription')
    supertitle = mapped('customFields', 'supertitle')
    video_still = mapped('videoStillURL')
    flv_url = mapped('FLVURL')

    expires = mapped_datetime('endDate')
    date_last_modified = mapped_datetime('lastModifiedDate')
    date_created = mapped_datetime('creationDate')
    date_first_released = mapped_datetime('publishedDate')

    fields = ",".join((
        'creationDate',
        'customFields',
        'economics',
        'endDate',
        'id',
        'itemState',
        'lastModifiedDate',
        'length',
        'linkText',
        'linkURL',
        'longDescription',
        'name',
        'playsTotal',
        'playsTrailingWeek',
        'publisheddate',
        'referenceId',
        'shortDescription',
        'tags',
        'thumbnailURL',
        'videoStillURL',
        'FLVURL',
    ))

    @classmethod
    def find_by_ids(class_, ids):
        ids = ','.join(str(i) for i in ids)
        return class_.get_connection().get_list(
            'find_videos_by_ids', class_, video_ids=ids,
            video_fields=class_.fields)

    @classmethod
    def find_modified(class_, from_date):
        from_date = int(from_date.strftime("%s")) / 60
        return class_.get_connection().get_list(
            'find_modified_videos', class_,
            from_date=from_date,
            video_fields=class_.fields,
            filter='PLAYABLE,DELETED,INACTIVE,UNSCHEDULED',
            sort_by='MODIFIED_DATE', sort_order='DESC')

    @property
    def related(self):
        result = []
        custom = self.data.get('customFields')
        if custom is None:
            return ()
        for i in range(1, 6):
            unique_id = custom.get('ref_link%s' % i)
            if unique_id is not None:
                content = zeit.cms.interfaces.ICMSContent(unique_id, None)
                if content is not None:
                    result.append(content)
        return tuple(result)

    @related.setter
    def related(self, value):
        if not value:
            value = ()
        custom = self.data.setdefault('customFields', {})

        for i in range(1, 6):
            custom['ref_link%i' % i] = ''
            custom['ref_title%i' % i] = ''
        for i, obj in enumerate(value, 1):
            metadata = zeit.cms.content.interfaces.ICommonMetadata(obj, None)
            if metadata is None:
                continue
            custom['ref_link%s' % i] = obj.uniqueId
            custom['ref_title%s' % i] = metadata.teaserTitle

    @property
    def year(self):
        try:
            modified = int(self.data.get('lastModifiedDate'))
        except (TypeError, ValueError):
            return None
        return datetime.datetime.fromtimestamp(modified/1000).year

    # XXX year.setter is missing

    def to_cms(self, video=None):
        if video is None:
            video = zeit.content.video.video.Video()
        for key in zeit.content.video.interfaces.IVideo:
            try:
                setattr(video, key, getattr(self, key))
            except AttributeError:
                pass
        return video

    @classmethod
    def from_cms(cls, video):
        instance = cls(data=dict(id='foo'))
        for key in zeit.content.video.interfaces.IVideo:
            try:
                setattr(instance, key, getattr(video, key))
            except AttributeError:
                pass
        # XXX
        date_last_modified = \
            zeit.cms.content.interfaces.ISemanticChange(
            video).last_semantic_change
        if date_last_modified is not None:
            instance.date_last_modified = date_last_modified
        return instance


class Playlist(Converter):

    zope.interface.implements(zeit.brightcove.interfaces.IPlaylist)
    type = 'playlist'
    id_prefix = 'pls' # for old-style asset IDs
    item_state = 'ACTIVE'
    fields = ",".join((
        'id',
        'name',
        'shortDescription',
        'thumbnailURL',
        'videoIds',
    ))

    @property
    def video_ids(self):
        return tuple('http://xml.zeit.de/brightcove-folder/video-%s' % id
                     for id in self.data['videoIds'])

    @classmethod
    def find_by_ids(class_, ids):
        ids = ','.join(str(i) for i in ids)
        return class_.get_connection().get_list(
            'find_playlists_by_ids', class_,
            playlist_fields=class_.fields,
            playlist_ids=ids)

    @classmethod
    def find_all(class_):
        return class_.get_connection().get_list(
            'find_all_playlists', class_,
            playlist_fields=class_.fields)

    def to_cms(self, playlist=None):
        if playlist is None:
            playlist = zeit.content.video.playlist.Playlist()
        for key in zeit.content.video.interfaces.IPlaylist:
            try:
                setattr(playlist, key, getattr(self, key))
            except AttributeError:
                pass
        return playlist

    @classmethod
    def from_cms(cls, playlist):
        instance = cls(data=dict(id='foo'))
        for key in zeit.content.video.interfaces.IPlaylist:
            try:
                setattr(instance, key, getattr(playlist, key))
            except AttributeError:
                pass
        return instance
