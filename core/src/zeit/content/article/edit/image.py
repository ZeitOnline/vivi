from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import LEGACY_DISPLAY_MODE_SOURCE
from zeit.content.article.edit.interfaces import LEGACY_VARIANT_NAME_SOURCE
import grokcore.component
import lxml.objectify
import zeit.cms.checkout.interfaces
import zeit.cms.content.reference
import zeit.content.article.edit.interfaces
import zeit.content.article.edit.reference
import zeit.content.article.interfaces
import zeit.content.image.interfaces
import zeit.edit.interfaces
import zope.lifecycleevent


class ImageReferenceProperty(
        zeit.cms.content.reference.SingleReferenceProperty):

    def __set__(self, instance, value):
        saved_attributes = {name: getattr(instance, name) for name in [
            '__name__',
            'display_mode',
            'variant_name',
            'set_manually',
        ]}

        super(ImageReferenceProperty, self).__set__(instance, value)

        for name, val in saved_attributes.items():
            setattr(instance, name, val)
        instance.is_empty = (value is None)
        instance._p_changed = True


class Image(zeit.content.article.edit.reference.Reference):

    grokcore.component.implements(zeit.content.article.edit.interfaces.IImage)
    type = 'image'

    references = ImageReferenceProperty('.', 'image')

    _display_mode = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'display_mode')

    _variant_name = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'variant_name')

    # XXX this is a stopgap to fix #11730. The proper solution involves
    # a real Reference object, see #10686.
    set_manually = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'set-manually',
        zeit.content.article.edit.interfaces.IImage['set_manually'])

    def __init__(self, *args, **kw):
        super(Image, self).__init__(*args, **kw)
        if self._display_mode is None:
            self.display_mode = self.display_mode
        if self._variant_name is None:
            self.variant_name = self.variant_name

    @property
    def display_mode(self):
        if self._display_mode is not None:
            return self._display_mode

        # backward compatibility by mapping old layout to display_mode
        layout = self.xml.get('layout', None)
        mapping = dict(list(LEGACY_DISPLAY_MODE_SOURCE(self)))
        if layout in mapping:
            return mapping[layout]

        return zeit.content.article.edit.interfaces.IImage[
            'display_mode'].default

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value

    @property
    def variant_name(self):
        if self._variant_name is not None:
            return self._variant_name

        # backward compatibility by mapping old layout to display_mode
        layout = self.xml.get('layout', None)
        mapping = dict(list(LEGACY_VARIANT_NAME_SOURCE(self)))
        if layout in mapping:
            return mapping[layout]

        return zeit.content.article.edit.interfaces.IImage[
            'variant_name'].default

    @variant_name.setter
    def variant_name(self, value):
        self._variant_name = value


class Factory(zeit.content.article.edit.reference.ReferenceFactory):

    produces = Image
    title = _('Image')


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.image.interfaces.IImage,
                            int)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_image(body, image, position):
    block = Factory(body)(position)
    block.references = (block.references.get(image)
                        or block.references.create(image))
    return block


@grokcore.component.adapter(zeit.content.article.edit.interfaces.IEditableBody,
                            zeit.content.image.interfaces.IImageGroup,
                            int)
@grokcore.component.implementer(zeit.edit.interfaces.IElement)
def factor_image_block_from_imagegroup(body, group, position):
    return factor_image_block_from_image(body, group, position)


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

    block = context.main_image_block
    if block is None or block.set_manually:
        return
    image = zeit.content.image.interfaces.IImages(context).image
    if image:
        image = block.references.get(image) or block.references.create(image)
    context.main_image = image


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
            if (not p.countchildren()
                and not (p.text and p.text.strip())
                and (not p.attrib or p.attrib.keys() == [
                    '{http://namespaces.zeit.de/CMS/cp}__name__'])):
                p.getparent().remove(p)
