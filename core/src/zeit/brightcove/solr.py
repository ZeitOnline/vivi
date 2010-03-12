# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import itertools
import pytz
import zeit.brightcove.content
import zeit.solr.interfaces
import zope

def _index_changed_videos_and_playlists():
    from_date = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=1)
    videos = zeit.brightcove.content.Video.find_modified(
        from_date=from_date)
    playlists = zeit.brightcove.content.Playlist.find_all()
    for content in itertools.chain(videos, playlists):
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
        

@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def index_changed_videos_and_playlists():
    _index_changed_videos_and_playlists()
