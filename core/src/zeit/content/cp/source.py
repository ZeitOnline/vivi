import zeit.cms.content.contentsource
import zeit.cms.content.sources
import zope.dottedname.resolve


class CPTypeSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.cp'
    config_url = 'cp-types-url'
    default_filename = 'cp-types.xml'
    attribute = 'name'


class CPExtraSource(zeit.cms.content.sources.XMLSource):
    product_configuration = 'zeit.content.cp'
    config_url = 'cp-extra-url'
    default_filename = 'cp-extras.xml'
    attribute = 'id'

    def isAvailable(self, node, context):
        # Avoid circular import
        from zeit.content.cp.interfaces import ICenterPage

        cp = ICenterPage(context, None)
        for_ = zope.dottedname.resolve.resolve(node.get('for'))
        return super().isAvailable(node, cp) and for_.providedBy(context.__parent__)


class CenterPageSource(zeit.cms.content.contentsource.CMSContentSource):
    name = 'zeit.content.cp'

    @property
    def check_interfaces(self):
        # Prevent circular import
        import zeit.content.cp.interfaces

        return (zeit.content.cp.interfaces.ICenterPage,)


centerPageSource = CenterPageSource()
