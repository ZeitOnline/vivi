# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import datetime
import gocept.runner
import persistent
import pytz
import zeit.brightcove.interfaces
import zeit.brightcove.solr
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
        zope.event.notify(zope.lifecycleevent.ObjectAddedEvent(obj))

    def get(self, key):
        return self._data.get(key)

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def update_from_brightcove(self):
        # getting the playlists seems to be much more likely to fail, and since
        # we want to take what we can get, we do it *after* we have processed
        # the videos (instead of combining both steps)
        self._update_videos()
        self._update_playlists()

    def _update_videos(self):
        from_date = (datetime.datetime.now(pytz.UTC)
                     - datetime.timedelta(hours=2))
        videos = zeit.brightcove.content.Video.find_modified(
            from_date=from_date)
        for x in videos:
            self._update_content(x)

    def _update_playlists(self):
        # XXX this is bad coupling, but as we don't want to assume that the
        # repository and Solr are in sync (then we could delete playlists from
        # Solr in our __delitem__()), this is the only place and time where we
        # can do this.
        zeit.brightcove.solr.delete_playlists()

        playlists = list(zeit.brightcove.content.Playlist.find_all())
        exists = set()
        for x in playlists:
            exists.add(x.__name__)
            self._update_content(x)

        for content in list(self.values()):
            if not zeit.brightcove.interfaces.IPlaylist.providedBy(content):
                continue
            if content.__name__ not in exists:
                del self[content.__name__]

    def _update_content(self, newcontent):
        current = self.get(newcontent.__name__)

        if current:
            curtime = zope.dublincore.interfaces.IDCTimes(current)
            bctime = zope.dublincore.interfaces.IDCTimes(newcontent)
            if curtime.modified and curtime.modified >= bctime.modified:
                return

            curdata = current.data.copy()
            curdata.pop('lastModifiedDate', None)
            newdata = newcontent.data.copy()
            newdata.pop('lastModifiedDate', None)
            if curdata == newdata:
                return

        self[newcontent.__name__] = newcontent


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def update_repository():
    repository = zope.component.getUtility(
        zeit.brightcove.interfaces.IRepository)
    repository.update_from_brightcove()
