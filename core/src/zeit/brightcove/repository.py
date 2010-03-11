# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import datetime
import persistent
import pytz
import zeit.brightcove.interfaces
import zeit.brightcove.content
import zope.container.contained
import zope.dublincore.interfaces
import zope.event
import zope.interface
import zope.lifecycleevent


class Repository(persistent.Persistent,
                 zope.container.contained.Contained):

    zope.interface.implements(zeit.brightcove.interfaces.IRepository)

    _type_class_map = {
        'video': zeit.brightcove.content.Video,
        'playlist': zeit.brightcove.content.Playlist
    }

    BRIGHTCOVE_CACHE_TIMEOUT = datetime.timedelta(minutes=5)

    def __init__(self):
        self._data = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        obj = None
        try:
            obj = self._data[key]
        except KeyError:
            pass
        else:
            times = zope.dublincore.interfaces.IDCTimes(obj, None)
            if times is None:
                obj = None
            else:
                now = datetime.datetime.now(pytz.UTC)
                if times.created + self.BRIGHTCOVE_CACHE_TIMEOUT < now:
                    obj = None
        if obj is not None:
            return obj
        obj = self._get_from_brightcove(key)
        if obj is None:
            raise KeyError(key)
        obj = zope.container.contained.contained(obj, self, key)
        return obj

    def __setitem__(self, key, obj):
        self._data[key] = obj

    def _get_from_brightcove(self, key):
        class_, id = self._parse_key(key)
        if class_ is None:
            return
        for obj in class_.find_by_ids([id]):
            # The brightcove API is rahter stupid and returns [None] instead of
            # [] when there is no result. *ARGH*
            if obj.data is not None:
                zope.event.notify(
                    zope.lifecycleevent.ObjectCreatedEvent(obj))
                return obj

    def _parse_key(self, key):
        if ':' in key:
            type_, id_ = key.split(':', 1)
            return self._type_class_map.get(type_), id_
        return None, None
