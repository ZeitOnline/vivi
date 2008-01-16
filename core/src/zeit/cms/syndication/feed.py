# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.etree

import gocept.lxml.objectify

import persistent

import zope.component
import zope.interface

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.util
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces


FEED_NS = zeit.cms.syndication.interfaces.FEED_NAMESPACE
FEED_TEMPLATE = u"<feed xmlns='%s'><title/><container/></feed>" % FEED_NS


class Feed(persistent.Persistent,
           zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeed,
        zeit.cms.content.interfaces.IXMLContent)

    title = zeit.cms.content.property.ObjectPathProperty('feed.title')
    object_limit = zeit.cms.content.property.ObjectPathProperty(
        'feed.object_limit')

    def __init__(self, xml_source=None, __name__=None, **data):
        apply_defaults = False
        if xml_source is None:
            apply_defaults = True
            self.xml = gocept.lxml.objectify.fromstring(FEED_TEMPLATE)
        else:
            self.xml = gocept.lxml.objectify.fromfile(xml_source)
        self.uniqueId = None
        self.__name__ = __name__
        if apply_defaults:
            zeit.cms.content.util.applySchemaData(
                self, zeit.cms.syndication.interfaces.IFeed, data,
                omit=('xml',))

    @property
    def xml_source(self):
        """See IXMLContent."""
        return lxml.etree.tostring(self.xml, pretty_print=True)

    def keys(self):
        for entry in self.iterentries():
            yield entry.get('href')

    def insert(self, position, content):
        content = zeit.cms.interfaces.ICMSContent(content)
        unique_id = content.uniqueId
        if unique_id is None:
            raise ValueError('Cannot add objects without uniqueId.')
        pin_map = self.pin_map()
        entry = self.xml.makeelement('{%s}block' % FEED_NS)
        self.entries.insert(position, entry)
        entry.set('href', unique_id)
        while self.object_limit and len(self) > self.object_limit:
            last = list(self.keys())[-1]
            self._remove_by_id(last)
        self.updateMetadata(content)
        self.restorePinning(pin_map)
        self._p_changed = True

    def remove(self, content):
        content = zeit.cms.interfaces.ICMSContent(content)
        unique_id = content.uniqueId
        self._remove_by_id(unique_id)

    def pinned(self, content):
        entry = self.entry_map[content.uniqueId]
        return entry.get('pinned') == 'true'

    def pin(self, content):
        entry = self.entry_map[content.uniqueId]
        entry.set('pinned', 'true')

    def unpin(self, content):
        entry = self.entry_map[content.uniqueId]
        entry.set('pinned', 'false')

    def updateOrder(self, order):
        entries = self.entry_map
        if set(order) != set(entries.keys()):
            raise ValueError("The order argument must contain the same "
                             "keys as the feed.")
        ordered = []
        for id in order:
            ordered.append(entries[id])
        self.entries.block = ordered
        self._p_changed = True

    def __len__(self):
        return len(list(self.keys()))

    def __iter__(self):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for unique_id in self.keys():
            yield repository.getContent(unique_id)

    def getPosition(self, content):
        content_id = content.uniqueId
        for id, key in enumerate(self.keys()):
            if key == content_id:
                return id + 1

    def updateMetadata(self, content):
        entry = self.entry_map[content.uniqueId]
        for name, utility in zope.component.getUtilitiesFor(
            zeit.cms.syndication.interfaces.IFeedMetadataUpdater):
            utility.update_entry(entry, content)

    # helpers and internal API:

    def iterentries(self):
        return self.entries.iterchildren(tag='{%s}block' % FEED_NS)

    @property
    def entry_map(self):
        return dict((entry.get('href'), entry) for entry in self.iterentries())

    def pin_map(self):
        return dict((id, entry.get('href'))
                    for id, entry in enumerate(self.iterentries())
                    if entry.get('pinned') == 'true')

    def restorePinning(self, pin_map):
        items = list(self.keys())
        index = 0
        order = []
        added = set()
        while items:
            entry = pin_map.get(index)
            if entry is None:
                entry = items.pop(0)
            index += 1
            if entry in added:
                continue
            order.append(entry)
            added.add(entry)
        self.updateOrder(order)

    @property
    def entries(self):
        return self.xml.container

    def _remove_by_id(self, unique_id):
        for entry in self.iterentries():
            if entry.get('href') == unique_id:
                parent = entry.getparent()
                del parent[entry.tag][parent.index(entry)]
                self._p_changed = True
                # An element can only occur once. So we're done.
                break
        else:
            raise ValueError("'%s' not in feed." % unique_id)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def feedFactory(context):
    feed = Feed(context.data)
    zeit.cms.interfaces.IWebDAVWriteProperties(feed).update(context.properties)
    return feed


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory('feed')
resourceFactory = zope.component.adapter(
    zeit.cms.syndication.interfaces.IFeed)(resourceFactory)



class CommonMetadataUpdater(object):

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def update_entry(self, entry, content):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)
        if metadata is None:
            return
        entry['supertitle'] = metadata.supertitle
        entry['title'] = metadata.teaserTitle
        entry['text'] = metadata.teaserText
        entry['byline'] = metadata.byline
        entry['short'] = ''
        entry['short']['title'] = metadata.shortTeaserTitle
        entry['short']['text'] = metadata.shortTeaserText
