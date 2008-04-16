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
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces


class Feed(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.cms.syndication.interfaces.IFeed)

    title = zeit.cms.content.property.ObjectPathProperty('.title')
    object_limit = zeit.cms.content.property.ObjectPathProperty(
        '.object_limit')

    default_template = u"""\
        <channel
          xmlns:xsd="http://www.w3.org/2001/XMLSchema"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xmlns:py="http://codespeak.net/lxml/objectify/pytype">
          <title/>
          <container/>
        </channel>
    """

    def __init__(self, *args, **kwargs):
        super(Feed, self).__init__(*args, **kwargs)
        if not self.object_limit:
            self.object_limit = 50

    @property
    def xml_source(self):
        """return source of feed."""
        # BBB deprecated
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
        entry = lxml.objectify.E.block(href=unique_id)
        self.entries.insert(position, entry)
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

    def hidden(self, content):
        entry = self.entry_map[content.uniqueId]
        return entry.get('hp_hide') == 'true'

    def hide(self, content):
        entry = self.entry_map[content.uniqueId]
        return entry.set('hp_hide', 'true')

    def show(self, content):
        entry = self.entry_map[content.uniqueId]
        return entry.set('hp_hide', 'false')

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
        return self.entries.iterchildren(tag='block')

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


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'channel')
resourceFactory = zope.component.adapter(
    zeit.cms.syndication.interfaces.IFeed)(resourceFactory)


class CommonMetadataUpdater(object):
    """Put information for ICommonMetadata into the channel."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    short_title_path = lxml.objectify.ObjectPath('.short.title')
    short_text_path = lxml.objectify.ObjectPath('.short.text')
    homepage_title_path = lxml.objectify.ObjectPath('.homepage.title')
    homepage_text_path = lxml.objectify.ObjectPath('.homepage.text')

    def update_entry(self, entry, content):
        metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)
        if metadata is None:
            return
        entry['supertitle'] = metadata.supertitle
        entry['title'] = metadata.teaserTitle
        entry['text'] = metadata.teaserText
        entry['byline'] = metadata.byline
        self.short_title_path.setattr(entry, metadata.shortTeaserTitle)
        self.short_text_path.setattr(entry, metadata.shortTeaserText)
        self.homepage_title_path.setattr(entry, metadata.hpTeaserTitle)
        self.homepage_text_path.setattr(entry, metadata.hpTeaserText)



class RelatedMetadataUpdater(object):
    """Put information from IRelated into the channel."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def update_entry(self, entry, content):
        related = zeit.cms.content.interfaces.IRelatedContent(content, None)
        if related is None:
            return
        if not related.related:
            return
        xml_repr = zeit.cms.content.interfaces.IXMLRepresentation(related)
        entry.append(xml_repr.xml)
