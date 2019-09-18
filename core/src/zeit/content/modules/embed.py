import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


class Embed(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IEmbed)

    url = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'url', zeit.content.modules.interfaces.IEmbed['url'])
