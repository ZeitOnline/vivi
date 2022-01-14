from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.content.reference import OverridableProperty
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.content.cp.blocks.block
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zope.interface
import zope.security.checker


@zope.interface.implementer(
    zeit.content.cp.interfaces.ILocalTeaserBlock)
class LocalTeaserBlock(
        zeit.content.cp.blocks.teaser.Layoutable,
        zeit.content.cp.blocks.block.Block):

    type = 'local-teaser'

    teaserSupertitle = OverridableProperty(
        zeit.content.cp.interfaces.ILocalTeaserBlock['teaserSupertitle'],
        original='_reference')
    teaserTitle = OverridableProperty(
        zeit.content.cp.interfaces.ILocalTeaserBlock['teaserTitle'],
        original='_reference')
    teaserText = OverridableProperty(
        zeit.content.cp.interfaces.ILocalTeaserBlock['teaserText'],
        original='_reference')

    _teaserSupertitle_local = ObjectPathAttributeProperty(
        '.', 'teaserSupertitle')
    _teaserTitle_local = ObjectPathAttributeProperty('.', 'teaserTitle')
    _teaserText_local = ObjectPathProperty('.local_teaserText')

    # We don't actually want teaser modules to be a list anymore (see ZO-215),
    # and it doesn't make sense in combination with local overrides anyway,
    # so we're only supporting referencing one content object here.
    _reference = zeit.cms.content.reference.SingleResource('.block', 'teaser')

    image = zeit.cms.content.reference.SingleResource('.local_image', 'image')
    fill_color = ObjectPathAttributeProperty('.', 'fill_color')

    # XXX copy&paste from TeaserBlock
    force_mobile_image = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'force_mobile_image', zeit.content.cp.interfaces.ITeaserBlock[
            'force_mobile_image'], use_default=True)

    def __iter__(self):
        content = self._reference
        if content is not None:
            yield TeaserOverrides(self, content)  # We could adapt if necessary

    def insert(self, position, content):
        self.append(content)

    def append(self, content):
        self._reference = content

    def remove(self, content):
        self._reference = None

    # IFeed for completeness

    def keys(self):
        content = self._reference
        if content:
            return (content.uniqueId,)
        else:
            return ()

    def __len__(self):
        return 1 if self._reference is not None else 0

    def __contains__(self, content):
        return self._reference == content

    def getPosition(self, content):
        return 1 if content in self else None

    def updateOrder(self, order):
        pass

    def updateMetadata(self, content):
        type(self)._reference.update_metadata(self)

    # end IFeed


class Factory(zeit.content.cp.blocks.block.BlockFactory):

    produces = LocalTeaserBlock
    title = _('Overridable teaser')


class TeaserReference(zeit.cms.content.reference.Reference):
    """The (default) `related` reference uses the `href` attribute to store
    the uniqueId; however centerpages have standardized on `uniqueId` (VIV-322)
    so we want to conform to that."""

    grok.name('teaser')

    @property
    def target_unique_id(self):
        return self.xml.get('uniqueId')

    def _update_target_unique_id(self):
        self.xml.set('uniqueId', self.target.uniqueId)


@grok.adapter(zeit.cms.interfaces.ICMSContent, name='teaser')
@grok.implementer(zeit.cms.content.interfaces.IXMLReference)
def teaser_reference(context):
    reference = lxml.objectify.E.reference()
    reference.set('uniqueId', context.uniqueId)
    updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(context)
    updater.update(reference, suppress_errors=True)
    return reference


class ITeaserOverrides(zope.interface.Interface):
    """Marker interface that gets applied directly, so that it is more
    specific than any content interfaces."""


class TeaserOverrides:
    """Wrapper around an ICommonMetadata object (that's referenced by a
    LocalTeaserBlock) that returns the block's values for locally overriden
    fields, and proxies everything else to the content object."""

    OVERRIDES = ['teaserSupertitle', 'teaserTitle', 'teaserText']

    def __init__(self, module, content):
        self.module = module
        self.content = content
        zope.interface.directlyProvides(
            self, ITeaserOverrides, zope.interface.providedBy(content))

    def __getattr__(self, name):
        if name not in self.OVERRIDES:
            return getattr(self.content, name)
        value = getattr(self.module, name)
        return value if value else getattr(self.content, name)


# Strictly readonly proxy. Bypass security, there's no good way to declare it.
zope.security.checker.BasicTypes[
    TeaserOverrides] = zope.security.checker.NoProxy


@grok.implementer(zeit.content.image.interfaces.IImages)
class OverrideImages(grok.Adapter):

    grok.context(ITeaserOverrides)

    image = OverridableProperty(
        zeit.content.image.interfaces.IImages['image'],
        original='_content')
    fill_color = OverridableProperty(
        zeit.content.image.interfaces.IImages['fill_color'],
        original='_content')

    def __init__(self, context):
        super().__init__(context)
        self._image_local = context.module.image
        self._fill_color_local = context.module.fill_color
        self._content = zeit.content.image.interfaces.IImages(context.content)
