from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.interface


class FrameBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(zeit.content.cp.interfaces.IFrameBlock)

    url = zeit.cms.content.property.ObjectPathProperty(
        '.url', zeit.content.cp.interfaces.IFrameBlock['url'])


zeit.edit.block.register_element_factory(
    [zeit.content.cp.interfaces.IArea],
    'frame', _('Frame block'))
