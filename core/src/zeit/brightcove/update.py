# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import grokcore.component
import pytz
import zeit.brightcove.interfaces
import zeit.brightcove.solr
import zeit.cms.repository.interfaces
import zope.component
import zope.container.contained
import zope.lifecycleevent


class Update(grokcore.component.GlobalUtility):

    grokcore.component.implements(zeit.brightcove.interfaces.IUpdate)

    folder = 'brightcove-folder'

    @property
    def dav(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @property
    def _data(self):
        return self.dav[self.folder]

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, obj):
        self._data[key] = obj

    def get(self, key):
        return self._data.get(key)

    def __call__(self):
        # getting the playlists seems to be much more likely to fail, and since
        # we want to take what we can get, we do it *after* we have processed
        # the videos (instead of combining both steps)
        self._update_videos()
        self._update_playlists()

    def _update_videos(self):
        now = datetime.datetime.now(pytz.UTC)
        from_date = (datetime.datetime(now.year, now.month, now.day, now.hour)
                     - datetime.timedelta(hours=10))
        videos = zeit.brightcove.content.Video.find_modified(
            from_date=from_date)
        for x in videos:
            self._update_video(x)

    def _update_playlists(self):
        playlists = zeit.brightcove.content.Playlist.find_all()
        exists = set()
        for playlist in playlists:
            exists.add(self._bc_name(playlist))
            self._update_playlist(playlist)

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for bc_name in list(repository['brightcove-folder'].keys()):
            if bc_name.startswith('playlist') and bc_name not in exists:
                del repository['brightcove-folder'][bc_name]

    def _update_video(self, bc_video):
        cms_video = zeit.cms.interfaces.ICMSContent(bc_video.uniqueId, None)
        if cms_video is None:
            self._add_object_to_cms(bc_video)
            return

        if bc_video.item_state == 'DELETED':
            self._delete_object_from_cms(bc_video)

        # Update video in CMS iff the BC version is newer. For easier
        # comparison between objects in CMS and BC, operate on BC
        # representations.
        current = bc_video.from_cms(cms_video)

        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        if (current.date_last_modified and bc_video.date_last_modified and
            current.date_last_modified >= bc_video.date_last_modified and
            current.video_still == bc_video.video_still):
            return

        # Only modify the object in DAV if it really changed in BC.
#        curdata = current.data.copy()
#        curdata.pop('lastModifiedDate', None)
        curdata = dict(name=current.data['name'])

#        newdata = bc_video.data.copy()
#        newdata.pop('lastModifiedDate', None)
        newdata = dict(name=bc_video.data['name'])

        if curdata == newdata:
            return

        with zeit.cms.checkout.helper.checked_out(cms_video) as co:
            bc_video.to_cms(co)

    def _update_playlist(self, bc_playlist):
        cms_playlist = zeit.cms.interfaces.ICMSContent(
            bc_playlist.uniqueId, None)
        if cms_playlist is None:
            self._add_object_to_cms(bc_playlist)
            return

        # Update video in CMS iff the BC version is newer. For easier
        # comparison between objects in CMS and BC, operate on BC
        # representations.
        current = bc_playlist.from_cms(cms_playlist)

        # Only modify the object in DAV if it really changed in BC.
#        curdata = current.data.copy()
        curdata = dict(name=current.data['name'])
#        newdata = bc_playlist.data.copy()
        newdata = dict(name=bc_playlist.data['name'])
        if curdata == newdata:
            return

        with zeit.cms.checkout.helper.checked_out(cms_playlist) as co:
            bc_playlist.to_cms(co)

    def _add_object_to_cms(self, bc_object):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['brightcove-folder'][self._bc_name(bc_object)] = \
            bc_object.to_cms()

    def _delete_object_from_cms(self, bc_object):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        del repository['brightcove-folder'][self._bc_name(bc_object)]

    def _bc_name(self, bc_object):
        return bc_object.uniqueId.rsplit('/', 1)[1]


@gocept.runner.appmain(ticks=120, principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def update_repository():
    repository = zope.component.getUtility(
        zeit.brightcove.interfaces.IRepository)
    repository.update_from_brightcove()
