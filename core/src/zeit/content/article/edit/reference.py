from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.schema


class Reference(zeit.edit.block.SimpleElement):

    area = zeit.content.article.edit.interfaces.IArticleArea
    grok.baseclass()

    is_empty = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'is_empty',
        zeit.content.article.edit.interfaces.IReference['is_empty'])

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
            updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                value, None)
            if updater is not None:
                updater.update(self.xml)

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
        block = super(ReferenceFactory, self).__call__(position)
        block.is_empty = True
        return block


class Gallery(Reference):

    grok.implements(
        zeit.content.article.edit.interfaces.IGallery)
    type = 'gallery'


class GalleryFactory(ReferenceFactory):

    produces = Gallery
    title = _('Gallery')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.gallery.interfaces.IGallery,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_gallery(body, context, position):
    block = GalleryFactory(body)(position)
    block.references = context
    return block


class Infobox(Reference):

    grok.implements(
        zeit.content.article.edit.interfaces.IInfobox)
    type = 'infobox'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zope.schema.TextLine(
            default=zeit.content.article.edit.interfaces.IInfobox[
                'layout'].default), use_default=True)


class InfoboxFactory(ReferenceFactory):

    produces = Infobox
    title = _('Infobox')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.infobox.interfaces.IInfobox,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_infobox(body, context, position):
    block = InfoboxFactory(body)(position)
    block.references = context
    return block


class Timeline(Reference):

    grok.implements(
        zeit.content.article.edit.interfaces.ITimeline)
    type = 'timeline'


class TimelineFactory(ReferenceFactory):

    produces = Timeline
    title = _('Timeline')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.article.edit.interfaces.ITimeline,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_timeline(body, context, position):
    block = TimelineFactory(body)(position)
    block.references = context
    return block


class Portraitbox(Reference):

    grok.implements(
        zeit.content.article.edit.interfaces.IPortraitbox)
    type = 'portraitbox'

    layout = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'layout', zope.schema.TextLine())

    _name_local = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'name_local',
        zeit.content.article.edit.interfaces.IPortraitbox['name'])
    name = zeit.cms.content.reference.OverridableProperty(
        zeit.content.portraitbox.interfaces.IPortraitbox['name'],
        original='references')

    _text_local = zeit.cms.content.property.Structure(
        '.text', zeit.content.article.edit.interfaces.IPortraitbox['text'])
    text = zeit.cms.content.reference.OverridableProperty(
        zeit.content.article.edit.interfaces.IPortraitbox['text'],
        original='references')

    def __init__(self, *args, **kw):
        super(Portraitbox, self).__init__(*args, **kw)
        if not self.layout:
            self.layout = zeit.content.article.edit.interfaces.IPortraitbox[
                'layout'].default


class PortraitboxFactory(ReferenceFactory):

    produces = Portraitbox
    title = _('Portraitbox')


@grok.adapter(zeit.content.article.edit.interfaces.IArticleArea,
              zeit.content.portraitbox.interfaces.IPortraitbox,
              int)
@grok.implementer(zeit.edit.interfaces.IElement)
def factor_block_from_portraitbox(body, context, position):
    block = PortraitboxFactory(body)(position)
    block.references = context
    return block


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_reference_metadata(article, event):
    body = zeit.content.article.edit.interfaces.IEditableBody(article)
    for block in body.values():
        if (zeit.content.article.edit.interfaces.IImage.providedBy(block) and
                block.references is not None):
            type(block).references.update_metadata(block)
        elif (zeit.content.article.edit.interfaces.IReference.providedBy(
                block) and block.references is not None):
            # Re-assigning the old value updates xml metadata
            block.references = block.references
