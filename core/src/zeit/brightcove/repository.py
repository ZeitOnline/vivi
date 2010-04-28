# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import datetime
import persistent
import pytz
import zeit.brightcove.interfaces
import zope.component
import zope.container.contained
import zope.interface


class Repository(persistent.Persistent,
                 zope.container.contained.Contained):

    zope.interface.implements(zeit.brightcove.interfaces.IRepository)

    def __init__(self):
        self._data = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, obj):
        self._data[key] = obj

    def get(self, key):
        return self._data.get(key)

    def update_from_brightcove(self):
        from_date = (datetime.datetime.now(pytz.UTC)
                     - datetime.timedelta(hours=2))
        videos = zeit.brightcove.content.Video.find_modified(
            from_date=from_date)
        for content in videos:
            current = self.get(content.__name__)
            curtime = zope.dublincore.interfaces.IDCTimes(current, None)
            bctime = zope.dublincore.interfaces.IDCTimes(content)
            if curtime and curtime.modified > bctime.modified:
                continue
            self[content.__name__] = content

        # separate into two loops, since getting the playlists is much more
        # likely to fail, so we want to take what we can get
        playlists = list(zeit.brightcove.content.Playlist.find_all())
        for content in playlists:
            self[content.__name__] = content
