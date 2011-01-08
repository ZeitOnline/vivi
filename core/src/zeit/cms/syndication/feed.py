# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import logging
import lxml.etree
import rwproperty
import zeit.cms.connector
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.cms.type
import zope.component
import zope.interface
import zope.location.location
import zope.proxy
import zope.security.proxy


log = logging.getLogger(__name__)


class Feed(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeed,
        zeit.cms.interfaces.IAsset)

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
        if not isinstance(zope.proxy.removeAllProxies(content), FakeEntry):
            content = zeit.cms.interfaces.ICMSContent(content)
        unique_id = content.uniqueId
        self._remove_by_id(unique_id)

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
        for unique_id in self.keys():
            try:
                yield zeit.cms.interfaces.ICMSContent(unique_id)
            except TypeError:
                entry = self.entry_map[unique_id]
                yield FakeEntry(unique_id, entry)

    def __contains__(self, obj):
        if not zeit.cms.interfaces.ICMSContent.providedBy(obj):
            return False
        return obj.uniqueId in self.entry_map

    def getPosition(self, content):
        content_id = content.uniqueId
        for id, key in enumerate(self.keys()):
            if key == content_id:
                return id + 1

    def updateMetadata(self, content):
        entry = self.entry_map[content.uniqueId]
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(content)
        updater.update(entry)

    def getMetadata(self, content):
        return zope.location.location.located(
            Entry(self.entry_map[content.uniqueId]), self)

    # helpers and internal API:

    def iterentries(self):
        return self.entries.iterchildren(tag='block')

    @property
    def entry_map(self):
        return dict((entry.get('href'), entry) for entry in self.iterentries())

    def pin_map(self):
        return dict((id, content.uniqueId)
                    for id, content in enumerate(self)
                    if self.getMetadata(content).pinned)

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
        __traceback_info__ = (self.uniqueId, )
        try:
            return self.xml['container']
        except AttributeError, e:
            log.error("Invalid channel XML format", exc_info=True)
            raise RuntimeError("Invalid channel XML format.")

    def _remove_by_id(self, unique_id):
        for entry in self.iterentries():
            if entry.get('href') == unique_id:
                parent = entry.getparent()
                parent.remove(entry)
                self._p_changed = True
                # An element can only occur once. So we're done.
                break
        else:
            raise ValueError("'%s' not in feed." % unique_id)


class FeedType(zeit.cms.type.XMLContentTypeDeclaration):

    interface = zeit.cms.syndication.interfaces.IFeed
    factory = Feed
    type = 'channel'
    title = _('Channel')
    addform = 'zeit.cms.syndication.feed.Add'

    def register_as_type(self, config):
        return config.hasFeature('zeit.cms.decentral-syndication')


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def feed_references(context):
    feed = zeit.cms.syndication.interfaces.IFeed(context, None)
    if not feed:
        return None
    return list(feed)


@zope.component.adapter(
    zeit.cms.syndication.interfaces.IFeed,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_feed_metadata_on_checkin(context, event):
    for item in context:
        context.updateMetadata(item)


class Entry(object):
    """An entry in the feed."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IEntry)

    def __init__(self, element):
        self.xml = element

    @rwproperty.getproperty
    def pinned(self):
        return self.xml.get('pinned') == 'true'

    @rwproperty.setproperty
    def pinned(self, value):
        self._set_bool('pinned', value)

    @rwproperty.getproperty
    def hidden(self):
        return self.xml.get('hp_hide') == 'true'

    @rwproperty.setproperty
    def hidden(self, value):
        self._set_bool('hp_hide', value)

    @rwproperty.getproperty
    def big_layout(self):
        return self.xml.get('layout') == 'big'

    @rwproperty.setproperty
    def big_layout(self, value):
        if value:
            self.xml.set('layout', 'big')
        else:
            self.xml.attrib.pop('layout', None)

    @rwproperty.getproperty
    def hidden_relateds(self):
        return self.xml.get('hidden_relateds') == 'true'

    @rwproperty.setproperty
    def hidden_relateds(self, value):
        self._set_bool('hidden_relateds', value)

    def _set_bool(self, attribute, value):
        if value:
            value = 'true'
        else:
            value = 'false'
        self.xml.set(attribute, value)


class FakeEntry(object):
    """Entry which does not reference an object in the CMS."""

    def __init__(self, id, entry):
        self.uniqueId = id
        self.title = unicode(entry.find('title'))


class FakeXMLReferenceUpdater(object):

    zope.component.adapts(FakeEntry)
    zope.interface.implements(zeit.cms.content.interfaces.IXMLReferenceUpdater)

    def __init__(self, context):
        pass

    def update(self, node):
        pass
