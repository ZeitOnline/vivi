from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.content.reference import OverridableProperty
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.interface
import zope.security.checker


@zope.interface.implementer(
    zeit.content.cp.interfaces.ILocalTeaserBlock)
class LocalTeaserBlock(zeit.content.cp.blocks.block.Block):

    type = 'local-teaser'

    # XXX copy&paste from TeaserBlock
    force_mobile_image = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'force_mobile_image', zeit.content.cp.interfaces.ITeaserBlock[
            'force_mobile_image'], use_default=True)

    def __init__(self, context, xml):
        super().__init__(context, xml)
        if self.xml.get('module') == 'teaser':
            if isinstance(self.layout, zeit.content.cp.layout.NoBlockLayout):
                raise ValueError(_(
                    'No default teaser layout defined for this area.'))
            self.layout = self.layout
        assert self.xml.get('module') != 'teaser'

    @property
    def layout(self):
        id = self.xml.get('module')
        source = zeit.content.cp.interfaces.ILocalTeaserBlock['layout'].source(
            self)
        layout = source.find(id)
        if layout:
            return layout
        return zeit.content.cp.interfaces.IArea(self).default_teaser_layout \
            or zeit.content.cp.layout.NoBlockLayout(self)

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)

    # end copy&paste

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


class TeaserOverrides:
    """Wrapper around an ICommonMetadata object (that's referenced by a
    LocalTeaserBlock) that returns the block's values for locally overriden
    fields, and proxies everything else to the content object."""

    OVERRIDES = zeit.content.cp.interfaces.IReadLocalTeaserBlock.names()

    def __init__(self, module, content):
        self.module = module
        self.content = content

    def __getattr__(self, name):
        if name not in self.OVERRIDES:
            return getattr(self.content, name)
        value = getattr(self.module, name)
        return value if value else getattr(self.content, name)


# Strictly readonly proxy. Bypass security, there's no good way to declare it.
zope.security.checker.BasicTypes[
    TeaserOverrides] = zope.security.checker.NoProxy
