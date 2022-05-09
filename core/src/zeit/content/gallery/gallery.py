from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import xml.sax.saxutils
import zeit.cms.content.dav
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.wysiwyg.html
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.location.location
import zope.security.proxy


# A gallery used to be a center page, that's why we initialize it with such a
# template.
GALLERY_TEMPLATE = """\
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body>
        <column layout="left"/>
        <column layout="right">
            <container/>
        </column>
    </body>
</gallery>"""


@zope.interface.implementer(
    zeit.content.gallery.interfaces.IGallery,
    zeit.cms.interfaces.IEditorialContent)
class Gallery(zeit.cms.content.metadata.CommonMetadata):
    """Gallery"""

    _image_folder = zeit.cms.content.property.SingleResource(
        '.head.image-folder')

    default_template = GALLERY_TEMPLATE

    zeit.cms.content.dav.mapProperties(
        zeit.content.gallery.interfaces.IGalleryMetadata,
        zeit.content.gallery.interfaces.DAV_NAMESPACE,
        ('type',))

    @property
    def xml_source(self):
        return lxml.etree.tostring(
            self.xml, 'UTF-8', xml_declaration=True, encoding=str)

    @property
    def image_folder(self):
        folder = self._image_folder
        if folder is None:
            folder = self._guess_image_folder()
            if folder is not None:
                self.image_folder = folder
        return folder

    @image_folder.setter
    def image_folder(self, value):
        self._image_folder = value
        self.reload_image_folder()

    def reload_image_folder(self):
        image_folder = self.image_folder
        if 'thumbnails' in image_folder:
            for name in image_folder['thumbnails']:
                del image_folder['thumbnails'][name]
        for name in image_folder:
            image = image_folder[name]
            entry = zeit.content.gallery.interfaces.IGalleryEntry(image, None)
            if entry is None:
                if name in self:
                    # Ignore all non image types
                    del self[name]
            else:
                if name in self:
                    # Update the existing entry
                    self[name] = self[name]
                else:
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
        entry.is_crop_of = node.get('is_crop_of')
        entry.title = node.find('title')
        if entry.title is not None:
            entry.title = str(entry.title)
        entry.text = node.find('text')
        if entry.text is None:
            entry.text = lxml.objectify.E.text()
        elif entry.text.text:
            # Hrm. There is text which is not wrapped in another node, wrap it.
            entry.text = lxml.objectify.E.text(
                lxml.objectify.E.p(entry.text.text,
                                   *entry.text.getchildren()))
        entry.layout = node.get('layout')
        if entry.layout is not None:
            entry.layout = str(entry.layout)

        gallery_caption = node.find('caption')
        if gallery_caption is not None:
            entry.caption = str(gallery_caption)

        # XXX need location information on the entry itself for crops(),
        # but just returning entry here breaks tests, so we do both for now.
        entry.__parent__ = self
        entry.__name__ = key
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
        if image_folder is None:
            return []
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
        return list(zip(list(self.keys()), list(self.values())))

    def __len__(self):
        return int(self._entries_container.xpath('count(block)'))

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
        try:
            return self.xml['body']['column'][1]['container']
        except Exception:
            # Probably means we're ITMSContent and don't have a whole body.
            return lxml.objectify.XML('<container/>')

    def _get_block_for_key(self, key):
        matching_blocks = self._entries_container.xpath(
            'block[@name=%s]' % xml.sax.saxutils.quoteattr(key))
        if matching_blocks:
            assert len(matching_blocks) == 1
            return matching_blocks[0]

        # This might be an old instance.
        matching_images = self._entries_container.xpath('block/image')
        new_id = None
        for image in matching_images:
            src = image.get('src')
            if src.startswith('/cms/work/'):
                new_id = src.replace('/cms/work/', 'http://xml.zeit.de/')
            elif src.startswith('http://xml.zeit.de/'):
                new_id = src
            if new_id is not None and src.endswith('/' + key):
                block = image.getparent()
                block.set('name', key)
                image.set('src', new_id)
                self._p_changed = True
                return block

    def _list_all_keys(self):
        return (str(x) for x in self._entries_container.xpath('block/@name'))

    def _guess_image_folder(self):
        # Ugh. We haven't got a folder? This could be an old gallery.
        image_sources = self._entries_container.xpath('block/image/@src')
        unique_id = None
        for path in image_sources:
            if path.startswith('/cms/work/'):
                unique_id = zeit.cms.interfaces.ID_NAMESPACE + path[10:]
            elif path.startswith(zeit.cms.interfaces.ID_NAMESPACE):
                unique_id = path
            if unique_id is not None:
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


class GalleryType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Gallery
    interface = zeit.content.gallery.interfaces.IGallery
    type = 'gallery'
    title = _('Gallery')


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.gallery.interfaces.IGalleryEntry)
def galleryentry_factory(context):
    entry = GalleryEntry()
    entry.image = context
    entry.thumbnail = zeit.content.image.interfaces.IPersistentThumbnail(
        context)
    entry.title = None
    entry.text = None
    entry.layout = None
    entry.is_crop_of = None

    # Prefill the caption with the image's caption
    metadata = zeit.content.image.interfaces.IImageMetadata(context)
    entry.caption = metadata.caption
    return entry


@zope.interface.implementer(zeit.content.gallery.interfaces.IGalleryEntry)
class GalleryEntry:

    @property
    def crops(self):
        result = []
        for entry in self.__parent__.values():
            if entry.is_crop_of == self.__name__:
                result.append(entry)
        return result


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
class EntryXMLRepresentation:

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        node = lxml.objectify.XML('<block/>')
        if self.context.title:
            node['title'] = self.context.title

        # Remove security proxy from lxml tree before inserting in the a
        # different tree
        node['text'] = zope.security.proxy.removeSecurityProxy(
            self.context.text)

        if self.context.caption:
            node.append(lxml.objectify.E.caption(self.context.caption))
        if self.context.is_crop_of:
            node.set('is_crop_of', self.context.is_crop_of)

        node['image'] = zope.component.getAdapter(
            self.context.image,
            zeit.cms.content.interfaces.IXMLReference, name='image')
        node['thumbnail'] = zope.component.getAdapter(
            self.context.thumbnail,
            zeit.cms.content.interfaces.IXMLReference, name='image')
        if self.context.layout:
            node.set('layout', self.context.layout)
        return node


@zope.component.adapter(zeit.content.gallery.interfaces.IGallery)
class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):

    def get_tree(self):
        # we can't express that 'body' is allowed for IGallery objects as a
        # security declaration, since that would have to apply to the objectify
        # element
        body = zope.security.proxy.removeSecurityProxy(self.context).xml.body
        try:
            text = body['text']
        except AttributeError:
            text = lxml.objectify.E.text()
            body.append(text)
        return text


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
class EntryHTMLContent(zeit.wysiwyg.html.HTMLContentBase):

    def get_tree(self):
        return self.context.text


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGalleryEntry,
    zope.lifecycleevent.IObjectModifiedEvent)
def update_gallery_on_entry_change(entry, event):
    entry.__parent__[entry.__name__] = entry


@zope.component.adapter(zeit.content.gallery.interfaces.IGallery)
def get_visible_entry_count_for_gallery(context):
    container = context._entries_container
    return len(container.xpath('block[not(@layout="hidden")]/@name'))


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(zeit.content.image.interfaces.IImageMetadata)
class EntryMetadata:
    """ImageMetadata composition from gallery entry and its image."""

    def __init__(self, context):
        self.context = context
        self._image_metadata = zeit.content.image.interfaces.IImageMetadata(
            context.image, None)

    def __getattr__(self, name):
        __traceback_info__ = (self.context.__name__, name)
        # Delegate attributes to ImageMetadata of entry image
        value = getattr(self.context, name, self)
        if value is self:  # Using self as a marker
            value = getattr(self._image_metadata, name)
        return value


@grok.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@grok.implementer(zeit.content.image.interfaces.IImages)
def images_for_entry(context):
    context.fill_color = None
    return context


@grok.implementer(zope.index.text.interfaces.ISearchableText)
class SearchableText(grok.Adapter):
    """SearchableText for a gallery."""

    grok.context(zeit.content.gallery.interfaces.IGallery)

    def getSearchableText(self):
        main_text = []
        for p in self.context.xml.body.xpath("//p"):
            text = str(p).strip()
            if text:
                main_text.append(text)
        return main_text
