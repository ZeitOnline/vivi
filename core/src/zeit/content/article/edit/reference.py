import grokcore.component as grok
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.references.references
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.edit.interfaces


class Reference(zeit.content.article.edit.block.Block):
    grok.baseclass()

    is_empty = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'is_empty', zeit.content.article.edit.interfaces.IReference['is_empty']
    )

    @property
    def references(self):
        return zeit.cms.interfaces.ICMSContent(self.xml.get('href'), None)

    @references.setter
    def references(self, value):
        if value is None:
            # clear everything to be sure we don't expose any false
            # informationn when another object is set later
            name = self.__name__
            self.xml.attrib.clear()
            self.is_empty = True
            self.__name__ = name
            for child in self.xml.getchildren():
                self.xml.remove(child)
        else:
            self._validate(value)
            self.is_empty = False
            self.xml.set('href', value.uniqueId)

    def _validate(self, value):
        field = zope.interface.providedBy(self).declared[0]['references']
        field = field.bind(self)
        field.validate(value)


@grok.adapter(zeit.content.article.edit.interfaces.IReference)
@grok.implementer(zeit.cms.content.interfaces.ICommonMetadata)
def find_commonmetadata(context):
    body = context.__parent__
    article = body.__parent__
    return article


class ReferenceFactory(zeit.content.article.edit.block.BlockFactory):
    grok.baseclass()

    def __call__(self, position=None):
        block = super().__call__(position)
        block.is_empty = True
        return block


@grok.implementer(zeit.content.article.edit.interfaces.IGallery)
class Gallery(Reference):
    type = 'gallery'


class GalleryFactory(ReferenceFactory):
    produces = Gallery
    title = _('Gallery')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea, zeit.content.gallery.interfaces.IGallery, int
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_gallery(body, context, position):
    block = GalleryFactory(body)(position)
    block.references = context
    return block


@grok.implementer(zeit.content.article.edit.interfaces.IInfobox)
class Infobox(Reference):
    type = 'infobox'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.',
        'layout',
        zope.schema.TextLine(
            default=zeit.content.article.edit.interfaces.IInfobox['layout'].default
        ),
        use_default=True,
    )


class InfoboxFactory(ReferenceFactory):
    produces = Infobox
    title = _('Infobox')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea, zeit.content.infobox.interfaces.IInfobox, int
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_infobox(body, context, position):
    block = InfoboxFactory(body)(position)
    block.references = context
    return block


@grok.implementer(zeit.content.article.edit.interfaces.IPortraitbox)
class Portraitbox(Reference):
    type = 'portraitbox'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zope.schema.TextLine()
    )

    _name_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'name_local', zeit.content.article.edit.interfaces.IPortraitbox['name']
    )
    name = zeit.cms.content.reference.OverridableProperty(
        zeit.content.portraitbox.interfaces.IPortraitbox['name'], original='references'
    )

    _text_local = zeit.cms.content.property.Structure(
        '.text', zeit.content.article.edit.interfaces.IPortraitbox['text']
    )
    text = zeit.cms.content.reference.OverridableProperty(
        zeit.content.article.edit.interfaces.IPortraitbox['text'], original='references'
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        if not self.layout:
            self.layout = zeit.content.article.edit.interfaces.IPortraitbox['layout'].default


class PortraitboxFactory(ReferenceFactory):
    produces = Portraitbox
    title = _('Portraitbox')


@grok.adapter(
    zeit.content.article.edit.interfaces.IArticleArea,
    zeit.content.portraitbox.interfaces.IPortraitbox,
    int,
)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_portraitbox(body, context, position):
    block = PortraitboxFactory(body)(position)
    block.references = context
    return block


@grok.subscribe(
    zeit.content.article.edit.interfaces.IPortraitbox, zope.lifecycleevent.IObjectModifiedEvent
)
def reset_local_properties(context, event):
    for description in event.descriptions:
        if (
            description.interface is zeit.content.article.edit.interfaces.IPortraitbox
            and 'references' in description.attributes
        ):
            break
    else:
        return
    value = context.references
    context.references = None
    if value is not None:
        context.references = value


class SingleResource(zeit.cms.content.reference.SingleResource):
    def __set__(self, instance, value):
        saved_attributes = {
            name: getattr(instance, name)
            for name in [
                '__name__',
            ]
        }

        super().__set__(instance, value)

        for name, val in saved_attributes.items():
            setattr(instance, name, val)
        instance._p_changed = True


class ExtractBodyReferences(zeit.cms.references.references.Extract):
    interface = zeit.content.article.interfaces.IArticle
    grok.name(interface.__name__)

    ATTRIBUTES = {
        zeit.content.article.edit.interfaces.IReference: 'references',
        zeit.content.article.edit.interfaces.IRawText: 'text_reference',
    }

    def __call__(self):
        result = []
        for module in self.content.body.filter_values(*self.ATTRIBUTES):
            target = self._get_reference_target(module)
            if target is not None:
                result.append({'target': target, 'type': 'article-body'})

        header = self.content.header.module
        if any(x.providedBy(header) for x in self.ATTRIBUTES):
            target = self._get_reference_target(header)
            if target is not None:
                result.append({'target': target, 'type': 'article-header'})

        return result

    def _get_reference_target(self, module):
        for iface, name in self.ATTRIBUTES.items():
            if iface.providedBy(module):
                value = getattr(module, name)
                if zeit.cms.content.interfaces.IReference.providedBy(value):
                    value = value.target
                return value
