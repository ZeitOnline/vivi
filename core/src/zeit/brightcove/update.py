import logging

import z3c.celery.celery
import zope.event
import zope.lifecycleevent

from zeit.brightcove.convert import DeletedVideo
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.workflow.interfaces import PRIORITY_LOW, IPublish, IPublishInfo
from zeit.content.video.interfaces import IVideo
import zeit.brightcove.convert
import zeit.brightcove.session
import zeit.cms.celery
import zeit.cms.cli
import zeit.cms.interfaces
import zeit.content.video.video


log = logging.getLogger(__name__)


class import_base:
    def _update(self):
        log.info('Updating %s', self.bcobj)
        # We overwrite last_semantic_change with the BC value.
        with zeit.cms.checkout.helper.checked_out(
            self.cmsobj, semantic_change=None, events=False
        ) as co:
            # Don't send events here, a full checkout/checkin cycle is done
            # during publish anyway, directly below (and so we don't publish
            # twice due to the publish_on_checkin handler).
            if co is None:
                log.warning('Could not checkout %s', self.cmsobj)
            else:
                self.bcobj.apply_to_cms(co)
                if IVideo.providedBy(co):  # XXX This factoring is kludgy
                    self._download_image(co)
                # This is a bit coarse, but it would be quite fiddly to
                # determine which attributes really have changed, and probably
                # not worth the effort anyway.
                zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(
                        co, zope.lifecycleevent.Attributes(IVideo, *list(IVideo))
                    )
                )


class import_video(import_base):
    """Updates the CMS state to the given BC state, by exactly one of:
    deleting the CMS object, retracting deactivated objects, adding a new CMS
    object or updating the existing CMS object.

    This is a class only to better organize the code.
    """

    cms_class = zeit.content.video.video.Video

    def __init__(self, bcobj):
        log.debug('Import for video %s', bcobj.uniqueId)
        self.bcobj = bcobj
        self.folder = self.bcobj.__parent__
        self.cmsobj = zeit.cms.interfaces.ICMSContent(self.bcobj.uniqueId, None)
        log.debug('CMS object resolved: %r', self.cmsobj)
        success = self.delete() or self.add() or self.update()
        if not success:
            log.warning('Not processed: %s', self.bcobj.uniqueId)

    def delete(self):
        if not isinstance(self.bcobj, DeletedVideo):
            return False
        elif self.cmsobj is None:
            # Deleted in BC and no CMS object: we're done.
            return True
        log.info('Deleting %s', self.bcobj)
        if IPublishInfo(self.cmsobj).published:
            IPublish(self.cmsobj).retract(background=False)
        del self.bcobj.__parent__[self.bcobj.id]
        still = zeit.content.image.interfaces.IImages(self.cmsobj).image
        if still is not None and still.__name__ == '%s-still' % self.bcobj.id:
            del still.__parent__[still.__name__]
        return True

    def add(self):
        if self.cmsobj is not None or self.bcobj.skip_import:
            return False
        self._add()
        if self.bcobj.state == 'ACTIVE':
            # XXX countdown is workaround race condition between celery/redis BUG-796
            IPublish(self.cmsobj).publish(priority=PRIORITY_LOW, countdown=5)
            log.info('Publishing %s' % self.bcobj.uniqueId)
        return True

    def _add(self):
        log.info('Adding %s', self.bcobj)
        cmsobj = self.cms_class()
        self.bcobj.apply_to_cms(cmsobj)
        # Special case of ObjectCreatedEvent, so that e.g. ISemanticChange is
        # preserved.
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(cmsobj, None))
        self.cmsobj = cmsobj
        self._download_image(cmsobj)
        self._commit()

    def _download_image(self, cmsobj):
        # since we cannot readily distinguish whether the image has changed
        # on BC side we *always* update the (master) image of the image group
        # but we only set the reference *to* that imagegroup if there isn't
        # already one in place.
        # this allows manual overrides by the editors to take prioty during
        # subsequent updates.
        if not FEATURE_TOGGLES.find('video_import_images'):
            return
        still = download_teaser_image(self.folder, self.bcobj.data, 'still')
        img = zeit.content.image.interfaces.IImages(cmsobj)
        if img.image is None and still is not None:
            img.image = still

    def _commit(self):
        self.folder[self.bcobj.id] = self.cmsobj
        self.cmsobj = self.folder[self.bcobj.id]

    def update(self):
        if self.bcobj.skip_import:
            return True
        self._update()
        if self.bcobj.state == 'ACTIVE':
            try:
                # XXX countdown is workaround race condition between celery/redis BUG-796
                IPublish(self.cmsobj).publish(priority=PRIORITY_LOW, countdown=5)
            except z3c.celery.celery.HandleAfterAbort as e:
                try:
                    error = e.c_args[0][1]  # Our API is a bit clumsy.
                except IndexError:
                    pass
                else:
                    if error.startswith('LockingError'):
                        pass
                    else:
                        raise
        else:
            log.info('Deactivating %s', self.bcobj)
            if IPublishInfo(self.cmsobj).published:
                IPublish(self.cmsobj).retract(background=False)
        return False


BC_IMG_KEYS = {'still': 'poster'}


def download_teaser_image(folder, bcdata, ttype='still'):
    name = '%s-%s' % (bcdata['id'], ttype)
    try:
        image = zeit.content.image.image.get_remote_image(
            bcdata['images'][BC_IMG_KEYS[ttype]]['src']
        )
    except Exception as exc:
        log.exception(exc)
        return None
    try:
        return zeit.content.image.imagegroup.ImageGroup.from_image(folder, name, image)
    except zope.app.locking.interfaces.LockingError:
        # don't bother to try to overwrite an image, that's
        # obviously being edited.
        return None


# Triggered by BC notification webhook, which we receive in
# zeit.brightcove.json.update.Notification
@zeit.cms.celery.task(queue='brightcove')
def import_video_async(video_id):
    import_video(zeit.brightcove.convert.Video.find_by_id(video_id))


def export_video(context, event):
    if event.publishing or FEATURE_TOGGLES.find('video_disable_export_on_checkin'):
        return
    session = zeit.brightcove.session.get()
    session.update_video(zeit.brightcove.convert.Video.from_cms(context))
