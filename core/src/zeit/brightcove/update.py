# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import pytz
import zeit.brightcove.content
import zeit.cms.repository.interfaces
import zope.component
import zope.container.contained
import zope.lifecycleevent


def update_from_brightcove():
    # getting the playlists seems to be much more likely to fail, and since
    # we want to take what we can get, we do it *after* we have processed
    # the videos (instead of combining both steps)
    VideoUpdater.update_all()
    PlaylistUpdater.update_all()


@gocept.runner.appmain(ticks=120, principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def update_repository():
    update_from_brightcove()


class BaseUpdater(object):

    def __init__(self, context):
        self.bcobj = context
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)

    def __call__(self):
        self.add() or self.delete() or self.update()

    @classmethod
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @classmethod
    def update_all(cls):
        for x in cls.get_objects():
            cls(x)()

    @classmethod
    def get_objects(cls):
        raise NotImplementedError()

    def add(self):
        if self.cmsobj is None:
            self.repository()['brightcove-folder'][
                self._bc_name(self.bcobj)] = self.bcobj.to_cms()
            return True

    def delete(self):
        pass

    def update(self):
        pass

    @classmethod
    def _bc_name(cls, bc_object):
        return bc_object.uniqueId.rsplit('/', 1)[1]


class VideoUpdater(BaseUpdater):

    @classmethod
    def get_objects(cls):
        now = datetime.datetime.now(pytz.UTC)
        from_date = (datetime.datetime(now.year, now.month, now.day, now.hour)
                     - datetime.timedelta(hours=10))
        return zeit.brightcove.content.Video.find_modified(from_date=from_date)

    def delete(self):
        if self.bcobj.item_state == 'DELETED':
            del self.repository()['brightcove-folder'][
                self._bc_name(self.bcobj)]
            return True

    def update(self):
        # Update video in CMS iff the BC version is newer. For easier
        # comparison between objects in CMS and BC, operate on BC
        # representations.
        current = self.bcobj.from_cms(self.cmsobj)

        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        if (current.date_last_modified and self.bcobj.date_last_modified and
            current.date_last_modified >= self.bcobj.date_last_modified and
            current.video_still == self.bcobj.video_still):
            return

        # Only modify the object in DAV if it really changed in BC.
#        curdata = current.data.copy()
#        curdata.pop('lastModifiedDate', None)
        curdata = dict(name=current.data['name'])
#        newdata = self.bcobj.data.copy()
#        newdata.pop('lastModifiedDate', None)
        newdata = dict(name=self.bcobj.data['name'])

        if curdata == newdata:
            return

        with zeit.cms.checkout.helper.checked_out(self.cmsobj) as co:
            self.bcobj.to_cms(co)
        return True


class PlaylistUpdater(BaseUpdater):

    @classmethod
    def get_objects(cls):
        return zeit.brightcove.content.Playlist.find_all()

    @classmethod
    def update_all(cls):
        objects = cls.get_objects()
        for x in objects:
            cls(x)()
        cls.delete_remaining_except(objects)

    def update(self):
        current = self.bcobj.from_cms(self.cmsobj)

#        curdata = current.data.copy()
        curdata = dict(name=current.data['name'])
#        newdata = self.bcobj.data.copy()
        newdata = dict(name=self.bcobj.data['name'])
        if curdata == newdata:
            return

        with zeit.cms.checkout.helper.checked_out(self.cmsobj) as co:
            self.bcobj.to_cms(co)
        return True

    @classmethod
    def delete_remaining_except(cls, existing):
        existing_names = [cls._bc_name(x) for x in existing]
        for name in list(cls.repository()['brightcove-folder'].keys()):
            if name.startswith('playlist') and name not in existing_names:
                del cls.repository()['brightcove-folder'][name]
