from zeit.content.cp.i18n import MessageFactory as _
import collections
import zc.sourcefactory.basic
import zeit.cms.content.sources
import zope.dottedname.resolve


class CPTypeSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-types-url'
    attribute = 'name'


class CPExtraSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-extra-url'
    attribute = 'id'

    def isAvailable(self, node, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import ICenterPage
        cp = ICenterPage(context, None)
        for_ = zope.dottedname.resolve.resolve(node.get('for'))
        return (super(CPExtraSource, self).isAvailable(node, cp) and
                for_.providedBy(context.__parent__))


class RSSTimeFormatSource(zc.sourcefactory.basic.BasicSourceFactory):

    values = collections.OrderedDict([
        ('none', _('None')),  # default
        ('date', _('Date')),
        ('time', _('Time')),
    ])

    def getValues(self):
        return self.values.keys()

    def getTitle(self, value):
        return self.values[value]
