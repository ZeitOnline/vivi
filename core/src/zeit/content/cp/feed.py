import logging
import os.path

import grokcore.component as grok
import lxml.builder
import lxml.etree
import zope.interface
import zope.location.location
import zope.proxy

import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.redirect.interfaces
import zeit.cms.type
import zeit.content.cp.interfaces


log = logging.getLogger(__name__)


class ContentList:
    """A feed contains a list of references to ICMSContent objects.

    These are stored as <block> tags, with the ``uniqueId`` attribute pointing
    to the referenced ICMSContent object. If this object in turn is only a
    reference (e.g. zeit.content.cp.teaser.XMLTeaser), the ``href`` attribute
    may contain the final resolved uniqueId to an actual content object
    (needed for XSLT since it can't perform this resolution).
    If the feed entry is does not reference another object, ``href`` equals
    ``uniqueId``.
    """

    object_limit = zeit.cms.content.property.ObjectPathProperty('.object_limit', zope.schema.Int())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.object_limit:
            self.object_limit = 50

    def keys(self):
        for entry in self.iterentries():
            # BBB Before uniqueId was introduced, href was authoritative.
            yield entry.get('uniqueId') or entry.get('href')

    def insert(self, position, content, suppress_errors=False):
        content = zeit.cms.interfaces.ICMSContent(content)
        unique_id = content.uniqueId
        if unique_id is None:
            raise ValueError('Cannot add objects without uniqueId.')
        pin_map = self.pin_map()
        entry = lxml.builder.E.block(uniqueId=unique_id, href=unique_id)
        self.entries.insert(position, entry)
        while self.object_limit and len(self) > self.object_limit:
            last = list(self.keys())[-1]
            self._remove_by_id(last)
        self.restorePinning(pin_map)
        self._p_changed = True

    def append(self, content):
        self.insert(len(list(self.keys())), content)

    def remove(self, content):
        if not isinstance(zope.proxy.removeAllProxies(content), FakeEntry):
            content = zeit.cms.interfaces.ICMSContent(content)
        unique_id = content.uniqueId
        self._remove_by_id(unique_id)

    def updateOrder(self, order):
        entries = self.entry_map
        if set(order) != set(entries.keys()):
            raise ValueError('The order argument must contain the same ' 'keys as the feed.')
        ordered = []
        for id in order:
            ordered.append(entries[id])
        for node in self.entries.iterchildren('block'):
            self.entries.remove(node)
        for node in ordered:
            self.entries.append(node)
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
        return None

    def getMetadata(self, content):
        return zope.location.location.located(Entry(self.entry_map[content.uniqueId]), self)

    # helpers and internal API:

    def iterentries(self):
        return self.entries.iterchildren(tag='block')

    @property
    def entry_map(self):
        # BBB Before uniqueId was introduced, href was authoritative.
        return {entry.get('uniqueId') or entry.get('href'): entry for entry in self.iterentries()}

    def pin_map(self):
        return {
            id: content.uniqueId
            for id, content in enumerate(self)
            if self.getMetadata(content).pinned
        }

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
        __traceback_info__ = (self.uniqueId,)
        result = self.xml.find('container')
        if result is None:
            log.error('Invalid channel XML format', exc_info=True)
            raise RuntimeError('Invalid channel XML format.')
        return result

    def _remove_by_id(self, unique_id):
        for entry in self.iterentries():
            # BBB Before uniqueId was introduced, href was authoritative.
            if (entry.get('uniqueId') or entry.get('href')) == unique_id:
                parent = entry.getparent()
                parent.remove(entry)
                self._p_changed = True
                # An element can only occur once. So we're done.
                break
        else:
            raise ValueError("'%s' not in feed." % unique_id)


@zope.interface.implementer(zeit.content.cp.interfaces.IFeed, zeit.cms.interfaces.IAsset)
class Feed(ContentList, zeit.cms.content.xmlsupport.XMLContentBase):
    title = zeit.cms.content.property.ObjectPathProperty('.title')

    default_template = """\
        <channel>
          <title/>
          <container/>
        </channel>
    """

    @property
    def xml_source(self):
        # BBB deprecated
        return lxml.etree.tostring(self.xml, pretty_print=True, encoding=str)


@zope.interface.implementer(zeit.content.cp.interfaces.IEntry)
class Entry:
    """An entry in the feed."""

    def __init__(self, element):
        self.xml = element

    @property
    def pinned(self):
        return self.xml.get('pinned') == 'true'

    @pinned.setter
    def pinned(self, value):
        self._set_bool('pinned', value)

    @property
    def hidden(self):
        return self.xml.get('hp_hide') == 'true'

    @hidden.setter
    def hidden(self, value):
        self._set_bool('hp_hide', value)

    @property
    def big_layout(self):
        return self.xml.get('layout') == 'big'

    @big_layout.setter
    def big_layout(self, value):
        if value:
            self.xml.set('layout', 'big')
        else:
            self.xml.attrib.pop('layout', None)

    @property
    def hidden_relateds(self):
        return self.xml.get('hidden_relateds') == 'true'

    @hidden_relateds.setter
    def hidden_relateds(self, value):
        self._set_bool('hidden_relateds', value)

    def _set_bool(self, attribute, value):
        if value:
            value = 'true'
        else:
            value = 'false'
        self.xml.set(attribute, value)


@zope.interface.implementer(
    zeit.cms.interfaces.ICMSContent, zeit.cms.content.interfaces.ICommonMetadata
)
class FakeEntry:
    """Entry which does not reference an object in the CMS."""

    def __init__(self, id, entry):
        for field in zeit.cms.content.interfaces.ICommonMetadata:
            setattr(self, field, None)
        self.uniqueId = id
        self.__name__ = os.path.basename(id)
        self.title = str(entry.find('title'))


@grok.implementer(zeit.cms.redirect.interfaces.IRenameInfo)
class FakeRenameInfo(grok.Adapter):
    grok.context(FakeEntry)

    previous_uniqueIds = ()


@zope.interface.implementer_only(zeit.connector.interfaces.IWebDAVProperties)
class FakeWebDAVProperties(grok.Adapter, dict):
    grok.context(FakeEntry)
