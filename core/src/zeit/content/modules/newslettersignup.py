import markdownify
import zeit.cms.content.property
import zeit.cms.content.sources
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


@zope.interface.implementer(
    zeit.content.modules.interfaces.INewsletterSignup)
class NewsletterSignup(zeit.edit.block.Element):

    newsletter = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'id'),
        zeit.content.modules.interfaces.INewsletterSignup['newsletter'])

    prefix_text = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty(
            '.', 'prefix_text'),
        zeit.content.modules.interfaces.INewsletterSignup['prefix_text'])

    @property
    def prefix(self):
        return markdownify.markdownify(self.prefix)