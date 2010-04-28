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
        self.delete_playlists()
        playlists = list(zeit.brightcove.content.Playlist.find_all())
        for content in playlists:
            self[content.__name__] = content

    def delete_playlists(self):
        """Playlists vanish from Brightcove when they are deleted (as opposed
        to Videos that use a 'deleted' state instead), so we need to
        pre-emptively delete them from our Repository, too.
        """
        for key, value in self.items():
            if zeit.brightcove.interfaces.IPlaylist.providedBy(value):
                del self[key]

        # XXX this is bad coupling, but as we don't want to assume that the
        # repository and Solr sare in sync (then we could delete playlists in
        # __delitem__()), this is the only place and time where we can do this
        zeit.brightcove.solr.delete_playlists()


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def update_repository():
    repository = zope.component.getUtility(
        zeit.brightcove.interfaces.IRepository)
    repository.update_from_brightcove()
