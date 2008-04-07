# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import xml.sax.saxutils

import lxml.etree
import lxml.objectify
import gocept.lxml.interfaces
import rwproperty

import zope.component
import zope.interface
import zope.lifecycleevent
import zope.location.location

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.util
import zeit.cms.repository.interfaces
import zeit.content.gallery.interfaces


# A gallery used to be a center page, that's why we initialize it with such a
# template.
GALLERY_TEMPLATE = u"""\
<centerpage xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body>
        <column layout="left"/>
        <column layout="right">
            <container/>
        </column>
    </body>
</centerpage>"""



class Gallery(zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(zeit.content.gallery.interfaces.IGallery)

    _image_folder = zeit.cms.content.property.SingleResource(
        '.head.image-folder')

    default_template = GALLERY_TEMPLATE

    @property
    def xml_source(self):
        return lxml.etree.tostring(self.xml, 'UTF-8', xml_declaration=True)

    @rwproperty.getproperty
    def image_folder(self):
        folder = self._image_folder
        if folder is None:
            folder = self._guess_image_folder()
            if folder is not None:
                self.image_folder = folder
        return folder

    @rwproperty.setproperty
    def image_folder(self, image_folder):
        self._image_folder = image_folder
        self.reload_image_folder()

    def reload_image_folder(self):
        image_folder = self.image_folder
        for name in image_folder:
            image = image_folder[name]
            entry = zeit.content.gallery.interfaces.IGalleryEntry(image, None)
            if entry is None:
                if name in self:
                    # Ignore all non image types
                    del self[name]
            else:
                if name not in self:
                    self[name] = entry

        for name in self._list_all_keys():
            if name not in image_folder:
                del self[name]

    # container interface

    def __getitem__(self, key):
        """Get a value for a key

        A KeyError is raised if there is no value for the key.
        """
        node = self._get_block_for_key(key)
        if node is None:
            raise KeyError(key)
        image_name = node.get('name')
        # What happens if the image goes away? A key-error is raised.
        image = self.image_folder[image_name]
        entry = zeit.content.gallery.interfaces.IGalleryEntry(image)
        entry.title = node.find('title')
        if entry.title is not None:
            entry.title = unicode(entry.title)
        entry.text = node.find('text')
        if entry.text is not None:
            entry.text = unicode(entry.text)
        return zope.location.location.located(entry, self, key)

    def __delitem__(self, key):
        block = self._get_block_for_key(key)
        if block is None:
            raise KeyError(key)
        block.getparent().remove(block)
        self._p_changed = True

    def get(self, key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        """Tell if a key exists in the mapping."""
        return self._get_block_for_key(key) is not None

    def keys(self):
        """Return the keys of the mapping object.
        """
        image_folder = self._image_folder
        return (name for name in self._list_all_keys()
                if name in image_folder)

    def __iter__(self):
        """Return an iterator for the keys of the mapping object.
        """
        return iter(self.keys())

    def values(self):
        """Return the values of the mapping object.
        """
        return (self[key] for key in self)

    def items(self):
        """Return the items of the mapping object.
        """
        return zip(self.keys(), self.values())

    def __len__(self):
        return self._entries_container.xpath('count(block)')

    def __setitem__(self, key, value):
        node = zeit.cms.content.interfaces.IXMLRepresentation(value).xml
        node.set('name', key)

        old_node = self._get_block_for_key(key)
        if old_node is None:
            self._entries_container.append(node)
        else:
            old_node.getparent().replace(old_node, node)

        self._p_changed = True

    def updateOrder(self, order):
        if set(self.keys()) != set(order):
            raise ValueError("The order argument must contain the same "
                             "keys as the container.")
        ordered = []
        for id in order:
            ordered.append(self._get_block_for_key(id))
        self._entries_container['block'] = ordered
        self._p_changed = True

    @property
    def _entries_container(self):
        return self.xml['body']['column'][1]['container']

    def _get_block_for_key(self, key):
        matching_blocks = self._entries_container.xpath(
            'block[@name=%s]' % xml.sax.saxutils.quoteattr(key))
        if matching_blocks:
            assert len(matching_blocks) == 1
            return matching_blocks[0]

        # This might be an old instance.
        matching_images = self._entries_container.xpath('block/image')
        for image in matching_images:
            if not image.get('src').startswith('/cms/work/'):
                continue
            if image.get('src').endswith('/' + key):
                block = image.getparent()
                block.set('name', key)
                image.set('src', image.get('src').replace(
                    '/cms/work/', 'http://xml.zeit.de/'))
                self._p_changed = True
                return block

    def _list_all_keys(self):
        return (unicode(name)
                for name in self._entries_container.xpath('block/@name'))

    def _guess_image_folder(self):
        # Ugh. We haven't got a folder? This could be an old gallery.
        image_sources = self._entries_container.xpath('block/image/@src')
        unique_id = None
        for path in image_sources:
            if not path.startswith('/cms/work'):
                continue
            unique_id = 'http://xml.zeit.de/%s' % path[9:]
            break
        if not unique_id:
            return

        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        try:
            image = repository.getContent(unique_id)
        except KeyError:
            return
        return image.__parent__


@zope.interface.implementer(zeit.content.gallery.interfaces.IGallery)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def galleryFactory(context):
    obj = Gallery(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVProperties(obj).update(context.properties)
    return obj


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'gallery')
resourceFactory = zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery)(resourceFactory)


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.gallery.interfaces.IGalleryEntry)
def galleryentry_factory(context):
    entry = GalleryEntry()
    entry.image = context
    entry.thumbnail = zeit.content.image.interfaces.IPersistentThumbnail(
        context)
    entry.title = None
    entry.text = u''
    return entry


class GalleryEntry(object):

    zope.interface.implements(zeit.content.gallery.interfaces.IGalleryEntry)


class EntryXMLRepresentation(object):

    zope.component.adapts(zeit.content.gallery.interfaces.IGalleryEntry)
    zope.interface.implements(zeit.cms.content.interfaces.IXMLRepresentation)

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        node = lxml.objectify.XML('<block/>')
        if self.context.title:
            node['title'] = self.context.title
        node['text'] = self.context.text
        node['image'] = zope.component.getAdapter(
            self.context.image, zeit.cms.content.interfaces.IXMLReference,
            name='image')
        node['thumbnail']  = zope.component.getAdapter(
            self.context.thumbnail, zeit.cms.content.interfaces.IXMLReference,
            name='image')
        return node


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGalleryEntry,
    zope.lifecycleevent.IObjectModifiedEvent)
def update_gallery_on_entry_change(entry, event):
    entry.__parent__[entry.__name__] = entry
