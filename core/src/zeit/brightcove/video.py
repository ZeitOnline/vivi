# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import persistent.mapping
import pybrightcove
import transaction
import zeit.brightcove.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.container.contained
import zope.interface



class mapped(object):

    def __init__(self, *path):
        assert path
        self.path = path

    def __get__(self, instance, class_):
        if instance is None:
            return self
        return self._get_from_dict(instance.data)

    def _get_from_dict(self, value):
        for key in self.path:
            value = value.get(key)
            if value is None:
                break
        return value

    def __set__(self, instance, value):
        data = instance.data
        for key in self.path[:-1]:
            data = data.setdefault(key, persistent.mapping.PersistentMapping())
        data[self.path[-1]] = value
        instance.save_to_brightcove()


class mapped_bool(mapped):

    def __get__(self, instance, class_):
        value = super(mapped_bool, self).__get__(instance, class_)
        return value == '1'

    def __set__(self, instance, value):
        value = '1' if value else '0'
        super(mapped_bool, self).__set__(instance, value)


class mapped_keywords(mapped):

    def __get__(self, instance, class_):
        value = super(mapped_keywords, self).__get__(instance, class_)
        if value:
            keywords = zope.component.getUtility(
                zeit.cms.content.interfaces.IKeywords)
            value = value.split(';')
            return tuple(keywords[code] for code in value if code in keywords)
        return ()

    def __set__(self, instance, value):
        if value:
            value = ';'.join(keyword.code for keyword in value)
        super(mapped_keywords, self).__set__(instance, value)


class Video(persistent.Persistent,
            zope.container.contained.Contained):

    zope.interface.implements(zeit.brightcove.interfaces.IVideo)

    data = None

    supertitle = mapped('customFields', 'supertitle')
    title = mapped('name')
    teaserText = mapped('shortDescription')
    subtitle = mapped('longDescription')
    ressort = mapped('customFields', 'ressort')
    serie = mapped('customFields', 'serie')
    product_id = mapped('customFields', 'produkt-id')
    keywords = mapped_keywords('customFields', 'cmskeywords')
    dailyNewsletter = mapped_bool('customFields', 'newsletter')
    banner = mapped_bool('customFields', 'banner')
    banner_id = mapped('customFields', 'banner-id')
    breaking_news = mapped_bool('customFields', 'breaking-news')
    has_recensions = mapped_bool('customFields', 'recensions')

    def __init__(self, data, connection=None):
        if data is not None:
            self.data = persistent.mapping.PersistentMapping(data)
            if 'customFields' in self.data:
                self.data['customFields'] = (
                    persistent.mapping.PersistentMapping(
                        self.data['customFields']))

    @staticmethod
    def get_connection():
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IAPIConnection)

    @classmethod
    def find_by_ids(class_, ids):
        ids = ','.join(str(i) for i in ids)
        return pybrightcove.ItemResultSet(
            'find_videos_by_ids', class_, class_.get_connection(),
            video_ids=ids)

    def save_to_brightcove(self):
        registered = getattr(self, '_v_save_hook_registered', False)
        if not registered:
            transaction.get().addBeforeCommitHook(self._save)
            self._v_save_hook_registered = True

    def _save(self):
        try:
            del self._v_save_hook_registered
        except AttribueError:
            pass
        __traceback_info__ = (self.data,)
        data = dict(self.data)
        if 'customFields' in data:
            data['customFields'] = dict(data['customFields'])
        self.get_connection().post('update_video', video=data)

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
        custom = self.data.setdefault('customFields',
                                      persistent.mapping.PersistentMapping())
        for i in range(1, 6):
            custom.pop('ref_link%i' % i, None)
            custom.pop('ref_title%i' % i, None)
        for i, obj in enumerate(value, 1):
            metadata  = zeit.cms.content.interfaces.ICommonMetadata(obj, None)
            if metadata is None:
                continue
            custom['ref_link%s' % i] = obj.uniqueId
            custom['ref_title%s' % i] = metadata.teaserTitle
