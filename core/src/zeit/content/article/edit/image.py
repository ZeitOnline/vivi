# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import gocept.lxml.interfaces
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

    @property
    def references(self):
        unique_id = self.xml.get('src')
        return zeit.cms.interfaces.ICMSContent(unique_id, None)

    @references.setter
    def references(self, value):
        node = zope.component.getAdapter(
            value, zeit.cms.content.interfaces.IXMLReference,
            name='image')
        # We have to save a few attributes before we replace the whole node
        name = self.__name__
        layout = self.layout
        self.xml.getparent().replace(self.xml, node)
        self.xml = node
        # Restore saved attributes
        self.__name__ = name
        self.layout =  layout
        self._p_changed = True


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

