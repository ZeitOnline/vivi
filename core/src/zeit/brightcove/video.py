# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import persistent.mapping
import pybrightcove
import zeit.brightcove.interfaces
import zope.container.contained
import zope.interface
import transaction



class mapped(object):

    def __init__(self, *path):
        assert path
        self.path = path

    def __get__(self, instance, class_):
        if instance is None:
            return self
        value = self._get_from_dict(instance.modified_data)
        if value is self:
            value = self._get_from_dict(instance.data)
        if value is self:
            raise AttributeError()
        return value

    def _get_from_dict(self, value):
        for key in self.path:
            value = value.get(key, self)
            if value is self:
                break
        return value

    def __set__(self, instance, value):
        data = instance.modified_data
        for key in self.path[:-1]:
            data = data.setdefault(key, {})
        data[self.path[-1]] = value
        instance.save_to_brightcove()


class mapped_bool(mapped):

    def __get__(self, instance, class_):
        value = super(mapped_bool, self).__get__(instance, class_)
        return value == '1'


class mapped_keywords(mapped):

    def __get__(self, instance, class_):
        value = super(mapped_keywords, self).__get__(instance, class_)
        return tuple(value.split(';'))


class Video(persistent.Persistent,
            zope.container.contained.Contained):

    zope.interface.implements(zeit.brightcove.interfaces.IVideo)

    supertitle = mapped('customFields', 'supertitle')
    title = mapped('name')
    teaserText = mapped('shortDescription')
    subtitle = mapped('longDescription')
    ressort = mapped('customFields', 'ressort')
    serie = mapped('customFields', 'serie')
    product_id = mapped('customFields', 'product-id')
    keywords = mapped_keywords('customFields', 'cmskeywords')
    # XXX related links
    dailyNewsletter = mapped_bool('customFields', 'newsletter')
    banner = mapped_bool('customFields', 'banner')
    banner_id = mapped('customFields', 'banner-id')
    breaking_news = mapped_bool('customFields', 'breaking-news')
    has_recensions = mapped_bool('customFields', 'recensions')

    def __init__(self, data, connection=None):
        self.data = data
        self.modified_data = persistent.mapping.PersistentMapping()

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
        self.get_connection().post('update_video', video=self.modified_data)
