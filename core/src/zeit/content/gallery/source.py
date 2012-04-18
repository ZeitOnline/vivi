# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.basic
import zeit.cms.content.sources


# XXX This was inspired b^W^Wcopied from zeit.content.cp, so some refactoring
# to extract a generic type source might be in order.
class GalleryTypeSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # we are contextual so we can set a default value, but have it not
    # validated at import time, since we don't have our product config then,
    # yet.

    product_configuration = 'zeit.content.gallery'
    config_url = 'gallery-types-url'

    def getValues(self, context):
        tree = self._get_tree()
        return [unicode(item.get('name'))
                for item in tree.iterchildren()]

    def getTitle(self, context, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        return unicode(tree.xpath('/gallery-types/type[@name = "%s"]' %
                                  value)[0])


class LayoutSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = {u'image-only': _('Image only'),
              u'hidden': _('Hidden'),
             }

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]

