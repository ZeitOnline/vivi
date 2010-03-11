# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import gocept.runner
import grokcore.component
import zeit.brightcove.content
import zeit.cms.interfaces
import zeit.solr.interfaces
import zope.component


def _index_changed_videos_and_playlists():
    from_date = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=1)
    videos = zeit.brightcove.content.Video.find_modified(
        from_date=from_date)
    for video in videos:
        zeit.solr.interfaces.IUpdater(video).update()


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.brightcove', 'index-principal'))
def index_changed_videos_and_playlists():
    _index_changed_videos_and_playlists()
