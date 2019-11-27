from zeit.cms.application import CONFIG_CACHE
import collections
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


class Newsletter(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, image, abo_text, anon_text ):
        super(Newsletter, self).__init__(id, title, image, abo_text, anon_text)
        self.id = id
        self.title = title
        self.image = image
        self.abo_text = abo_text
        self.anon_text = anon_text


class NewsletterSignupSource(zeit.cms.content.sources.ObjectSource,
                             zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.modules'
    config_url = 'newslettersignup-source'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        result = collections.OrderedDict()
        tree = self._get_tree()
        for node in tree.iterchildren('*'):
            newsletter = Newsletter(
                unicode(node.get('id')),
                unicode(node.get('title')),
                unicode(node.get('image')),
                unicode(node.get('abo_text')),
                unicode(node.get('anon_text'))
            )
            result[newsletter.id] = newsletter
        return result