# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import pybrightcove
import zeit.brightcove.interfaces
import zope.container.contained
import zope.interface



class mapped(object):

    def __init__(self, *path):
        assert path
        self.path = path

    def __get__(self, instance, class_):
        if instance is None:
            return self
        value = instance.data
        for key in self.path:
            if not isinstance(value, dict):
                raise AttributeError()
            value = value.get(key, self)
        if value is self:
            raise AttributeError()
        return value


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



    def __init__(self, data, connection=None):
        self.data = data

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
