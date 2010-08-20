# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.brightcove.interfaces
import zeit.solr.interfaces
import zope.component
import zope.lifecycleevent.interfaces


class Updater(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(zeit.solr.interfaces.IUpdater)

    def update(self, solr=''):
        # NOTE: The solr argument is ignored. update() alwas updates the
        # default, internal solr and the public solr.
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


class Index(object):

    grokcore.component.implements(zeit.solr.interfaces.IIndex)

    interface = zeit.brightcove.interfaces.IVideo

    def process(self, value, node):
        child_node = lxml.objectify.E.field(value, name=self.solr_field_name)
        lxml.objectify.deannotate(child_node)
        node.append(child_node)

    @property
    def solr_field_name(self):
        return getattr(self.__class__, 'grokcore.component.directive.name')


class FLVURLIndex(Index, grokcore.component.GlobalUtility):

    grokcore.component.name('h264_url')
    attribute = 'flv_url'


class BannerIndex(Index, grokcore.component.GlobalUtility):

    grokcore.component.name('banner')
    attribute = 'banner'


class BannerIDIndex(Index, grokcore.component.GlobalUtility):

    grokcore.component.name('banner-id')
    attribute = 'banner_id'
