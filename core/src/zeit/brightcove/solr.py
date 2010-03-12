# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import pytz
import zeit.brightcove.content
import zeit.solr.interfaces
import zeit.solr.query
import zope


def _index_changed_videos_and_playlists():
    from_date = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=1)
    videos = zeit.brightcove.content.Video.find_modified(from_date=from_date)
    for content in videos:
        _update_single_content(content)
    playlists = list(zeit.brightcove.content.Playlist.find_all())
    # we don't get the item_state on playlists, so this is necessary:
    _empty_playlists()
    for content in playlists:
        _update_single_content(content)


def _update_single_content(content):
    deleter = zope.component.getAdapter(
         content.uniqueId, zeit.solr.interfaces.IUpdater,
         name='delete')
    updater = zeit.solr.interfaces.IUpdater(content)

    if content.item_state == "ACTIVE":
        updater.update()
        updater.update(solr='public')
    elif content.item_state == 'INACTIVE':
        updater.update()
        deleter.update(solr='public')
    else:
        deleter.update()
        deleter.update(solr='public')

def _empty_playlists():
    query = zeit.solr.query.field(
        'type', 'zeit.brightcove.interfaces.IPlaylist')
    query = query.encode('UTF-8')
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    public_solr= zope.component.getUtility(
        zeit.solr.interfaces.ISolr, name='public')
    solr.delete(q=query, commit=False)
    public_solr.delete(q=query, commit=False)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def index_changed_videos_and_playlists():
    _index_changed_videos_and_playlists()
