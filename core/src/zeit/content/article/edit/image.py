# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


class Image(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IEditableBody
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IImage)
    type = 'image'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zeit.content.article.edit.interfaces.IImage['layout'])

    _custom_caption = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'custom-caption',
        zeit.content.article.edit.interfaces.IImage['custom_caption'])

    @property
    def references(self):
        # the IXMLReference of type 'image' could be for both,
        # IImage (src attribute) or IImageGroup (base-id attribute)
        unique_id = self.xml.get('src') or self.xml.get('base-id')
        return zeit.cms.interfaces.ICMSContent(unique_id, None)

    @references.setter
    def references(self, value):
        node = zope.component.getAdapter(
            value, zeit.cms.content.interfaces.IXMLReference,
            name='image')
        # We have to save a few attributes before we replace the whole node
        name = self.__name__
        layout = self.layout
        custom_caption = self.custom_caption
        self.xml.getparent().replace(self.xml, node)
        self.xml = node
        # Restore saved attributes
        self.__name__ = name
        self.layout = layout
        if custom_caption:
            self.custom_caption = custom_caption
        self._p_changed = True

    @property
    def custom_caption(self):
        return self._custom_caption

    @custom_caption.setter
    def custom_caption(self, value):
        self._custom_caption = value
        self.xml['bu'] = value


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Image
    title = _('Image')


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.image.interfaces.IImage)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_image(body, image):
    block = Factory(body)()
    block.references = image
    return block


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.image.interfaces.IImageGroup)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_imagegroup(body, group):
    block = Factory(body)()
    block.references = group
    return block


@grokcore.component.subscribe(
    zeit.content.article.interfaces.IArticle,
    zope.lifecycleevent.IObjectModifiedEvent)
def copy_image_to_body(context, event):
    for description in event.descriptions:
        if (description.interface is zeit.content.image.interfaces.IImages
            and 'image' in description.attributes):
            break
    else:
        return

    image = zeit.content.image.interfaces.IImages(context).image
    if image is None:
        return

    body = zeit.content.article.edit.interfaces.IEditableBody(context)

    try:
        image_block = body.values()[0]
    except IndexError:
        return
    if not zeit.content.article.edit.interfaces.IImage.providedBy(image_block):
        return
    if image_block.references is not None:
        return

    image_block.references = image


@grokcore.component.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def migrate_image_nodes_inside_p(article, event):
    while True:
        images = article.xml.xpath('//body//p//image')
        if not images:
            break
        for image in images:
            p = image.getparent()
            p.addprevious(image)
            if image.tail:
                # boah.
                stripped = lxml.objectify.XML(
                    lxml.etree.tostring(image, encoding=unicode).rsplit(
                        image.tail, 1)[0])
                p.addnext(getattr(lxml.objectify.E, p.tag)(image.tail))
                lxml.objectify.deannotate(p.getnext())
                image.getparent().replace(image, stripped)
            if not (p.countchildren() or
                    p.text and p.text.strip() or
                    p.attrib):
                p.getparent().remove(p)
