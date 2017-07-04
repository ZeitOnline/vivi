from zeit.brightcove.convert2 import DeletedVideo
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import logging
import zeit.brightcove.convert2
import zeit.brightcove.session
import zeit.cms.interfaces
import zeit.content.video.video


log = logging.getLogger(__name__)


class import_video(object):
    """Updates the CMS state to the given BC state, by exactly one of:
    deleting the CMS object, adding a new CMS object or updating the existing
    CMS object.

    This is a class only to better organize the code.
    """

    def __init__(self, bcobj):
        log.debug('Import for video %s', bcobj.uniqueId)
        self.bcobj = bcobj
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)
        log.debug('CMS object resolved: %r', self.cmsobj)
        success = (self.delete() or self.deactivate() or
                   self.add() or self.update())
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
            IPublish(self.cmsobj).retract(async=False)
        del self.bcobj.__parent__[self.bcobj.id]
        return True

    def deactivate(self):
        if self.bcobj.state != 'INACTIVE' or self.cmsobj is None:
            return False
        log.info('Deactivating %s', self.bcobj)
        if IPublishInfo(self.cmsobj).published:
            IPublish(self.cmsobj).retract(async=False)

    def add(self):
        if self.cmsobj is not None or self.bcobj.skip_import:
            return False
        log.info('Adding %s', self.bcobj)
        folder = self.bcobj.__parent__
        video = zeit.content.video.video.Video()
        self.bcobj.apply_to_cms(video)
        folder[self.bcobj.id] = video
        self.cmsobj = folder[self.bcobj.id]
        if self.bcobj.state == 'ACTIVE':
            IPublish(self.cmsobj).publish(async=False)
        return True

    def update(self):
        if self.bcobj.skip_import:
            return True
        log.info('Updating %s', self.bcobj)
        # We overwrite last_semantic_change with the BC value.
        with zeit.cms.checkout.helper.checked_out(
                self.cmsobj, semantic_change=None, events=False) as co:
            # Don't send events here, a full checkout/checkin cycle is done
            # during publish anyway, directly below (and so we don't publish
            # twice due to the publish_on_checkin handler).
            if co is None:
                log.warning('Could not checkout %s', self.cmsobj)
            else:
                self.bcobj.apply_to_cms(co)
        if self.bcobj.state == 'ACTIVE':
            IPublish(self.cmsobj).publish(async=False)


def export_video(context, event):
    if not event.publishing:
        session = zeit.brightcove.session.get()
        session.update_video(zeit.brightcove.convert2.Video.from_cms(context))


def publish_on_checkin(context, event):
    # prevent infinite loop, since there is a checkout/checkin cycle during
    # publishing (to update XML references etc.)
    if not event.publishing:
        zeit.cms.workflow.interfaces.IPublish(context).publish()
