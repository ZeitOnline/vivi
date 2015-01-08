from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zeit.cms.content.sources


class GalleryTypeSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.gallery'
    config_url = 'gallery-types-url'
    attribute = 'name'


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {
        u'image-only': _('Image only'),
        u'hidden': _('Hidden'),
    }

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]
