import grokcore.component as grok
import lxml.etree
import zope

from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class ImageGridProperties:
    def __init__(
        self,
        path,
        xml_reference_name,
        names=[],
        result_type=tuple,
        sorted=lambda x: x,
        used_types=[],
    ):
        self.names = names
        assert len(names) == len(used_types)
        self.xml_reference_name = xml_reference_name
        self.result_type = result_type
        self.sorted = sorted

    def __get__(self, instance, class_):
        tree = instance.xml
        result = []
        for index, row in enumerate(tree.xpath('//rows/*')):
            row_data = []
            for attr in row.attrib.values():
                row_data.append(attr)

            images = []
            for image in row.xpath('./image'):
                reference = zope.component.queryMultiAdapter(
                    (instance, image),
                    zeit.cms.content.interfaces.IReference,
                    name=self.xml_reference_name,
                )
                images.append(reference.target)

            if images:
                row_data.append(tuple(images))
            else:
                # append empty tuple ;)
                row_data.append(tuple())

            result.append(tuple(row_data))

        return tuple(result)

    def __set__(self, instance, value):
        # Save different things:
        # 1. display-mode
        # 2. variant-name
        # 3. images (in later episode!)
        tree = instance.xml
        # Add new nodes:
        value = self.sorted(value)
        rows_parent = tree.find('rows')
        if rows_parent is None:
            rows_parent = lxml.etree.Element('rows')
            tree.append(rows_parent)
        # remove all elements from 'rows'
        for row in rows_parent.xpath('*'):
            rows_parent.remove(row)

        for row_index, row_items in enumerate(value):
            row_tag = 'row'
            row_node = lxml.etree.Element(row_tag)
            rows_parent.append(row_node)

            row_node.clear()

            for col_index, item in enumerate(row_items):
                if isinstance(item, tuple):
                    for image_index, image in enumerate(item):
                        image_node = lxml.etree.Element('image')
                        # TODO: This is very naive, but it is working. I don't know how to
                        # generalize this.
                        image_node.set('base-id', image.uniqueId)
                        image_node.set('type', image.master_image.split('.')[1])
                        row_node.append(image_node)
                else:
                    row_node.set(self.names[col_index], item)


@grok.implementer(zeit.content.article.edit.interfaces.IImageGrid)
class ImageGrid(zeit.content.article.edit.block.Block):
    type = 'image_grid'

    def __init__(self, context, xml):
        # call base constructor
        super(ImageGrid, self).__init__(context, xml)
        if not self.xml.xpath('//rows'):
            self.xml.append(lxml.etree.Element('rows'))

    show_caption = ObjectPathAttributeProperty(
        '.', 'show_caption', zeit.content.article.edit.interfaces.IImageGrid['show_caption']
    )
    show_source = ObjectPathAttributeProperty(
        '.', 'show_source', zeit.content.article.edit.interfaces.IImageGrid['show_source']
    )

    rows = ImageGridProperties(
        path='.rows.row_1.image',
        names=['display_mode', 'variant_name', 'images'],
        xml_reference_name='image',
        used_types=[str, str, tuple],
    )


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = ImageGrid
    title = _('Image Grid')
