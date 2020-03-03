from zeit.brightcove.convert import DeletedVideo
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.video.interfaces import IVideo
import gocept.runner
import logging
import zeit.brightcove.convert
import zeit.brightcove.session
import zeit.cms.celery
import zeit.cms.interfaces
import zeit.content.video.playlist
import zeit.content.video.video
import zope.event
import zope.lifecycleevent


log = logging.getLogger(__name__)


class import_video(object):
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
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)
        log.debug('CMS object resolved: %r', self.cmsobj)
        success = (self.delete() or self.add() or self.update())
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
        return True

    def add(self):
        if self.cmsobj is not None or self.bcobj.skip_import:
            return False
        self._add()
        self._publish()
        return True

    def _publish(self):
        if self.bcobj.state == 'ACTIVE':
            IPublish(self.cmsobj).publish(background=False)
            if self.cmsobj.cms_thumbnail is not None:
                IPublish(self.cmsobj.cms_thumbnail).publish(background=False)
            if self.cmsobj.cms_video_still is not None:
                IPublish(self.cmsobj.cms_video_still).publish(background=False)

    def _add(self):
        log.info('Adding %s', self.bcobj)
        cmsobj = self.cms_class()
        self.bcobj.apply_to_cms(cmsobj)
        # Special case of ObjectCreatedEvent, so that e.g. ISemanticChange is
        # preserved.
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(cmsobj, None))
        self.cmsobj = cmsobj
        self._handle_teasers()
        self._commit()

    def _handle_teasers(self):
        cms_video_still = download_teaser_image(
            self.folder, self.bcobj.data, 'still')
        self.cmsobj.cms_video_still = cms_video_still
        cms_thumbnail = download_teaser_image(
            self.folder, self.bcobj.data, 'thumbnail')
        self.cmsobj.cms_thumbnail = cms_thumbnail

    def _commit(self):
        self.folder[self.bcobj.id] = self.cmsobj
        self.cmsobj = self.folder[self.bcobj.id]

    def update(self):
        if self.bcobj.skip_import:
            return True
        self._update()
        if self.bcobj.state == 'ACTIVE':
            IPublish(self.cmsobj).publish(background=False)
        else:
            log.info('Deactivating %s', self.bcobj)
            if IPublishInfo(self.cmsobj).published:
                IPublish(self.cmsobj).retract(background=False)

    def _update(self):
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
                # This is a bit coarse, but it would be quite fiddly to
                # determine which attributes really have changed, and probably
                # not worth the effort anyway.
                zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(
                        co, zope.lifecycleevent.Attributes(
                            IVideo, *list(IVideo))))


class migrate_video(import_video):

    """ subclass with slimmer init to act as helper
    for migration code
    """

    def __init__(self, bcobj, cmsobj, ):
        self.bcobj = bcobj
        self.cmsobj = cmsobj
        self.folder = self.cmsobj.__parent__


BC_IMG_KEYS = {
    'still': 'poster',
    'thumbnail': 'thumbnail'
}


def download_teaser_image(folder, bcdata, ttype='still'):
    name = '%s-%s' % (bcdata['id'], ttype)
    if name in folder:
        return folder[name]
    try:
        image = zeit.content.image.image.get_remote_image(
            bcdata['images'][BC_IMG_KEYS[ttype]]['src'])
    except Exception as exc:
        log.error(exc)
        image = None
    return zeit.brightcove.convert.image_group_from_image(
        folder,
        name,
        image)


# Triggered by BC notification webhook, which we receive in
# zeit.brightcove.json.update.Notification
@zeit.cms.celery.task(queuename='brightcove')
def import_video_async(video_id):
    import_video(zeit.brightcove.convert.Video.find_by_id(video_id))


def export_video(context, event):
    if not event.publishing:
        session = zeit.brightcove.session.get()
        session.update_video(zeit.brightcove.convert.Video.from_cms(context))


def publish_on_checkin(context, event):
    # prevent infinite loop, since there is a checkout/checkin cycle during
    # publishing (to update XML references etc.)
    if not event.publishing:
        zeit.cms.workflow.interfaces.IPublish(context).publish()


class import_playlist(import_video):
    # Inheriting from import_video is only mechanical, so we can reuse
    # _add() and _update(), we actually don't have anything else in common.

    cms_class = zeit.content.video.playlist.Playlist

    def __init__(self, bcobj):
        log.debug('Import for playlist %s', bcobj.uniqueId)
        self.bcobj = bcobj
        self.cmsobj = zeit.cms.interfaces.ICMSContent(
            self.bcobj.uniqueId, None)
        self.folder = self.cmsobj.__parent__
        log.debug('CMS object resolved: %r', self.cmsobj)
        success = self.add() or self.update()
        if not success:
            log.warning('Not processed: %s', self.bcobj.uniqueId)

    def add(self):
        if self.cmsobj is not None:
            return False
        self._add()
        IPublish(self.cmsobj).publish(background=False)
        return True

    def update(self):
        lsc = zeit.cms.content.interfaces.ISemanticChange(
            self.cmsobj).last_semantic_change
        if self.bcobj.updated_at <= lsc:
            return False
        self._update()
        IPublish(self.cmsobj).publish(background=False)

    @classmethod
    def generate_actions(cls):
        """Fulfills the gocept.runner.transaction_per_item API by returning an
        iterable of callables.
        """
        playlists = zeit.brightcove.convert.Playlist.find_all()
        for item in playlists:
            yield lambda: cls(item)
        yield lambda: cls.delete_except(playlists)

    @classmethod
    def delete_except(cls, known):
        """There is no way in the BC API to get data about deleted playlists,
        so we fall back on deleting any playlist that BC does not know about.
        """
        if not known:  # safetybelt
            return
        folder = zeit.brightcove.convert.playlist_location(None)
        cms_names = set(folder.keys())
        bc_names = set(x.id for x in known)
        for name in cms_names - bc_names:
            log.info('Deleting <Playlist id=%s>', name)
            cmsobj = folder[name]
            if IPublishInfo(cmsobj).published:
                IPublish(cmsobj).retract(background=False)
            del folder[name]


@gocept.runner.appmain(ticks=120, principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def import_playlists():
    log.info('Update run started')
    _import_playlists()
    log.info('Update run finished')


@gocept.runner.transaction_per_item
def _import_playlists():
    return import_playlist.generate_actions()
