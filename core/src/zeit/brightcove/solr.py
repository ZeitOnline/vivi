# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.brightcove.interfaces
import zeit.solr.interfaces
import zeit.solr.query
import zope
import zope.lifecycleevent.interfaces


class Updater(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(zeit.solr.interfaces.IUpdater)

    def update(self):
        updater = zope.component.getAdapter(
            self.context, zeit.solr.interfaces.IUpdater, name='update')
        deleter = zope.component.getAdapter(
            self.context.uniqueId, zeit.solr.interfaces.IUpdater,
            name='delete')

        # XXX this conditional looks strange, see #7161
        if self.context.item_state == "ACTIVE":
            updater.update()
            updater.update(solr='public')
        elif self.context.item_state == 'INACTIVE':
            deleter.update()
            deleter.update(solr='public')
        else:
            deleter.update()
            deleter.update(solr='public')


@grokcore.component.subscribe(
    zeit.brightcove.interfaces.IVideo,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def index_video_on_change(context, event):
    zeit.solr.interfaces.IUpdater(context).update()


def delete_playlists():
    query = zeit.solr.query.field(
        'type', 'zeit.brightcove.interfaces.IPlaylist')
    query = query.encode('UTF-8')
    solr = zope.component.getUtility(zeit.solr.interfaces.ISolr)
    public_solr= zope.component.getUtility(
        zeit.solr.interfaces.ISolr, name='public')
    solr.delete(q=query, commit=False)
    public_solr.delete(q=query, commit=False)
