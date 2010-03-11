# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.runner
import itertools
import pytz
import zeit.brightcove.content
import zeit.solr.interfaces


def _index_changed_videos_and_playlists():
    from_date = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=1)
    videos = zeit.brightcove.content.Video.find_modified(
        from_date=from_date)
    playlists = zeit.brightcove.content.Playlist.find_all()
    for video in itertools.chain(videos, playlists):
        zeit.solr.interfaces.IUpdater(video).update()


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def index_changed_videos_and_playlists():
    _index_changed_videos_and_playlists()
