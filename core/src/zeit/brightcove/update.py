# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import grokcore.component as grok
import itertools
import logging
import pytz
import zeit.addcentral.interfaces
import zeit.brightcove.converter
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.component


log = logging.getLogger(__name__)


@gocept.runner.transaction_per_item
def update_from_brightcove():
    # getting the playlists seems to be much more likely to fail, and since
    # we want to take what we can get, we do it *after* we have processed
    # the videos (instead of combining both steps)
    return itertools.chain(
        VideoUpdater.update_all(),
        PlaylistUpdater.update_all())


@gocept.runner.appmain(ticks=120, principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def _update_from_brightcove():
    log.info('Update run started')
    update_from_brightcove()
    log.info('Update run finished')


class BaseUpdater(grok.Adapter):

    grok.baseclass()
    grok.implements(zeit.brightcove.interfaces.IUpdate)

    publish_priority = zeit.cms.workflow.interfaces.PRIORITY_DEFAULT

    def __init__(self, context):
        log.debug('%r(%s)', self, context.uniqueId)
        self.publish_job_id = None
        self.bcobj = context
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)
        log.debug('CMS object resolved: %r', self.cmsobj)

    def __call__(self):
        success = self.delete() or self.add() or self.update()
        if not success:
            log.warning('Object %s not processed.', self.bcobj.uniqueId)

    @classmethod
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    @classmethod
    def update_all(cls):
        for x in cls.get_objects():
            cls.publish_priority = zeit.cms.workflow.interfaces.PRIORITY_LOW
            yield cls(x)

    @classmethod
    def get_objects(cls):
        raise NotImplementedError()

    def add(self):
        if self.cmsobj is None:
            log.info('Adding %s', self.bcobj)
            log.debug('Getting add location')
            folder = zeit.addcentral.interfaces.IAddLocation(self.bcobj)
            log.debug('Adding ...')
            folder[str(self.bcobj.id)] = self.bcobj.to_cms()
            self.cmsobj = folder[str(self.bcobj.id)]
            log.debug('Create publish job')
            self._publish_if_allowed()
            self.changed = True
            return True

    def delete(self):
        pass

    def update(self):
        pass

    def _update_cmsobj(self):
        log.info('Updating %s', self.bcobj)
        with zeit.cms.checkout.helper.checked_out(
            self.cmsobj, semantic_change=True, events=False) as co:
            # We don't need to send events here as a full checkout/checkin
            # cycle is done during publication anyway, below.
            if co is None:
                log.warning('Could not update %s' % self.cmsobj)
            else:
                self.bcobj.to_cms(co)
        self._publish_if_allowed()

    def _publish_cmsobj(self):
        info = zeit.cms.workflow.interfaces.IPublicationStatus(self.cmsobj)
        if info.published in ('not-published', 'published-with-changes'):
            self._publish_if_allowed()

    def _publish_if_allowed(self):
        self.publish_job_id = zeit.cms.workflow.interfaces.IPublish(
            self.cmsobj).publish(self.publish_priority)


class VideoUpdater(BaseUpdater):

    grok.context(zeit.brightcove.converter.Video)

    @classmethod
    def get_objects(cls):
        now = datetime.datetime.now(pytz.UTC)
        from_date = (datetime.datetime(now.year, now.month, now.day, now.hour)
                     - datetime.timedelta(hours=10))
        return zeit.brightcove.converter.Video.find_modified(
            from_date=from_date)

    def delete(self):
        if self.bcobj.item_state == 'ACTIVE':
            # Handled elsewhere
            return False
        if self.bcobj.item_state == 'DELETED' and self.cmsobj is None:
            # Deleted in BC and no CMS object. We're done.
            return True
        if self.bcobj.item_state == 'INACTIVE' and self.cmsobj is None:
            # The item needs to be imported (but must not be published)
            return False
        if zeit.cms.workflow.interfaces.IPublishInfo(
                self.cmsobj).published:
            log.info('Retracting %s', self.bcobj)
            zeit.cms.workflow.interfaces.IPublish(self.cmsobj).retract(
                zeit.cms.workflow.interfaces.PRIORITY_LOW)
        elif self.bcobj.item_state == 'DELETED':
            log.info('Deleting %s', self.bcobj)
            del self.cmsobj.__parent__[self.cmsobj.__name__]
        return True

    def update(self):
        # Update video in CMS iff the BC version is newer.
        new = self.bcobj.to_cms()
        changed = True

        # A bug in Brightcove may cause the last-modified date to remain
        # unchanged even when the video-still URL is actually changed.
        # (Also note that Brightcove has the misfeature of sometimes returning
        # old data for several minutes even directly after we POSTed to update
        # something.)
        current_mtime = zeit.cms.content.interfaces.ISemanticChange(
            self.cmsobj).last_semantic_change
        new_mtime = zeit.cms.content.interfaces.ISemanticChange(
            new).last_semantic_change
        if self.bcobj.ignore_for_update:
            changed = False
        elif (current_mtime and new_mtime and current_mtime >= new_mtime and
            self.cmsobj.video_still == new.video_still):
            changed = False
        if changed:
            self._update_cmsobj()
        self._publish_cmsobj()
        self.changed = changed
        return True

    def _publish_if_allowed(self):
        if self.bcobj.item_state == 'ACTIVE':
            super(VideoUpdater, self)._publish_if_allowed()


class PlaylistUpdater(BaseUpdater):

    grok.context(zeit.brightcove.converter.Playlist)

    @classmethod
    def get_objects(cls):
        return zeit.brightcove.converter.Playlist.find_all()

    @classmethod
    def update_all(cls):
        objects = cls.get_objects()
        for x in objects:
            cls.publish_priority = zeit.cms.workflow.interfaces.PRIORITY_LOW
            yield cls(x)
        yield lambda: cls.delete_remaining_except(objects)

    def update(self):
        current = self.bcobj.from_cms(self.cmsobj)
        changed = False

        curdata = current.data
        newdata = self.bcobj.data
        for key in self.bcobj.fields.split(','):
            if key == 'id':
                continue
            if curdata.get(key) != newdata.get(key):
                changed = True
                break

        if changed:
            self._update_cmsobj()
        self._publish_cmsobj()
        self.changed = changed
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
                zeit.cms.workflow.interfaces.IPublish(cmsobj).retract(
                    zeit.cms.workflow.interfaces.PRIORITY_LOW)
            else:
                del folder[name]
