import zeit.cms.content.sources
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


class NewsletterSignup(zeit.edit.block.Element):

    zope.interface.implements(
        zeit.content.modules.interfaces.INewsletterSignup)

    newsletter = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'id'),
        zeit.content.modules.interfaces.INewsletterSignup['newsletter'])
