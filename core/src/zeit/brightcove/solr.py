# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.brightcove.interfaces
import zeit.solr.interfaces
import zeit.solr.query
import zope.component
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
    zeit.brightcove.interfaces.IBrightcoveContent,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def index_content_on_change(context, event):
    index_content(context)


def index_content(context):
    zeit.solr.interfaces.IUpdater(context).update()


class FLVURLIndex(grokcore.component.GlobalUtility):

    grokcore.component.implements(zeit.solr.interfaces.IIndex)
    grokcore.component.name('flv_url')

    interface = zeit.brightcove.interfaces.IVideo
    attribute = 'flv_url'
    name = 'h264_url'

    def process(self, value, node):
        child_node = lxml.objectify.E.field(value, name=self.name)
        lxml.objectify.deannotate(child_node)
        node.append(child_node)
