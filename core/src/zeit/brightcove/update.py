# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import logging
import pytz
import zeit.addcentral.interfaces
import zeit.brightcove.converter
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.video.interfaces
import zope.component


log = logging.getLogger(__name__)


def update_from_brightcove():
    # getting the playlists seems to be much more likely to fail, and since
    # we want to take what we can get, we do it *after* we have processed
    # the videos (instead of combining both steps)
    VideoUpdater.update_all()
    PlaylistUpdater.update_all()


@gocept.runner.appmain(ticks=120, principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def _update_from_brightcove():
    update_from_brightcove()


class BaseUpdater(object):

    def __init__(self, context):
        self.bcobj = context
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)

    def __call__(self):
        self.delete() or self.add() or self.update()

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
            log.info('Adding %s', self.bcobj)
            folder = zeit.addcentral.interfaces.IAddLocation(self.bcobj)
            folder[str(self.bcobj.id)] = self.bcobj.to_cms()
            cmsobj = folder[str(self.bcobj.id)]
            zeit.cms.workflow.interfaces.IPublish(cmsobj).publish()
            return True

    def delete(self):
        pass

    def update(self):
        pass


class VideoUpdater(BaseUpdater):

    @classmethod
    def get_objects(cls):
        now = datetime.datetime.now(pytz.UTC)
        from_date = (datetime.datetime(now.year, now.month, now.day, now.hour)
                     - datetime.timedelta(hours=10))
        return zeit.brightcove.converter.Video.find_modified(
            from_date=from_date)

    def delete(self):
        if self.bcobj.item_state == 'DELETED':
            if self.cmsobj is None:
                # Deleted in BC and no CMS object. We're done.
                return True
            log.info('Deleting %s', self.bcobj)
            if zeit.cms.workflow.interfaces.IPublishInfo(
                    self.cmsobj).published:
                zeit.cms.workflow.interfaces.IPublish(self.cmsobj).retract()
            folder = zeit.addcentral.interfaces.IAddLocation(self.bcobj)
            del folder[str(self.bcobj.id)]
            return True

    def update(self):
        # Update video in CMS iff the BC version is newer.
        new = self.bcobj.to_cms()

        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        # (Also note that Brightcove has the misfeature of sometimes returning
        # old data for several minutes even directly after we POSTed to update
        # something.)
        current_mtime = zeit.cms.content.interfaces.ISemanticChange(
            self.cmsobj).last_semantic_change
        new_mtime = zeit.cms.content.interfaces.ISemanticChange(
            new).last_semantic_change

        if (current_mtime and new_mtime and current_mtime >= new_mtime and
            self.cmsobj.video_still == new.video_still):
            return

        # Only modify the object in DAV if it really changed in BC.
        for name in zeit.content.video.interfaces.IVideo:
            if getattr(self.cmsobj, name, None) != getattr(new, name, None):
                break
        else:
            return

        log.info('Updating %s', self.bcobj)
        with zeit.cms.checkout.helper.checked_out(
            self.cmsobj, semantic_change=True, events=False) as co:
            # We don't need to send events here as a full checkout/checkin
            # cycle is done duing publication anyway.
            self.bcobj.to_cms(co)
        zeit.cms.workflow.interfaces.IPublish(self.cmsobj).publish()
        return True


class PlaylistUpdater(BaseUpdater):

    @classmethod
    def get_objects(cls):
        return zeit.brightcove.converter.Playlist.find_all()

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

        log.info('Updating %s', self.bcobj)
        with zeit.cms.checkout.helper.checked_out(self.cmsobj) as co:
            self.bcobj.to_cms(co)
        zeit.cms.workflow.interfaces.IPublish(self.cmsobj).publish()
        return True

    @classmethod
    def delete_remaining_except(cls, bc_objects):
        if not bc_objects:
            return
        folder = zeit.addcentral.interfaces.IAddLocation(
            iter(bc_objects).next())
        cms_names = set(folder.keys())
        bc_names = set(str(x.id) for x in bc_objects)
        for name in cms_names - bc_names:
            log.info('Deleting <Playlist id=%s>', name)
            cmsobj = folder[name]
            if zeit.cms.workflow.interfaces.IPublishInfo(cmsobj).published:
                zeit.cms.workflow.interfaces.IPublish(cmsobj).retract()
            del folder[name]
