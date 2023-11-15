import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.contentsource
import zeit.cms.content.sources
import zope.interface
import zope.schema.interfaces


class IWhitelistSource(zope.schema.interfaces.IIterableSource):
    """Tag whitelist"""


class WhitelistSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    # this should be in .interfaces, but that leads to a circular import
    # between zeit.cms.content.interfaces and .interfaces

    # this is only contextual so we can customize the source_class

    @zope.interface.implementer(
        IWhitelistSource, zeit.cms.content.contentsource.IAutocompleteSource
    )
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def get_check_types(self):
            """IAutocompleteSource"""
            return ['tag']

        def __contains__(self, value):
            # XXX stopgap until we find out about #12609
            return True

    @property
    def whitelist(self):
        import zeit.cms.tagging.interfaces

        return zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)

    def getTitle(self, context, value):
        return value.label

    def getToken(self, context, value):
        return value.code


class ILocationSource(zope.schema.interfaces.IIterableSource):
    """Available locations."""


class LocationSource(zc.sourcefactory.contextual.BasicContextualSourceFactory):
    @zope.interface.implementer(ILocationSource, zeit.cms.content.contentsource.IAutocompleteSource)
    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def get_check_types(self):
            """IAutocompleteSource, but not applicable for us"""
            return []

        def __contains__(self, value):
            # We do not want to ask the whitelist again.
            return True

    def search(self, term):
        from zeit.cms.tagging.interfaces import IWhitelist  # circular import

        whitelist = zope.component.getUtility(IWhitelist)
        return whitelist.locations(term)


locationSource = LocationSource()
