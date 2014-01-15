# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.contextual
import zc.sourcefactory.source
import zeit.cms.content.contentsource
import zeit.cms.content.sources
import zope.interface
import zope.schema.interfaces


class IWhitelistSource(zope.schema.interfaces.IIterableSource):
    """Tag whitelist"""


class WhitelistSource(
        zc.sourcefactory.contextual.BasicContextualSourceFactory):

    # this should be in .interfaces, but that leads to a circular import
    # between zeit.cms.content.interfaces and .interfaces

    # this is only contextual so we can customize the source_class

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        zope.interface.implements(
            IWhitelistSource,
            zeit.cms.content.contentsource.IAutocompleteSource)

        def get_check_types(self):
            """IAutocompleteSource"""
            return ['tag']

        def __contains__(self, value):
            # XXX stopgap until we find out about #12609
            return True

    @property
    def whitelist(self):
        import zeit.cms.tagging.interfaces
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

    def getValues(self, context):
        return self.whitelist.values()

    def getTitle(self, context, value):
        return value.label

    def getToken(self, context, value):
        return value.code


class ILocationSource(zope.schema.interfaces.IIterableSource):
    pass


class LocationSource(
        zeit.cms.content.sources.SimpleXMLSourceBase,
        zc.sourcefactory.contextual.BasicContextualSourceFactory):

    # At the moment Locations are those tags in the whitelist that are
    # locations. The whitelist is cached on a timeout-basis, but we want the
    # locations to be cached, too, since filtering all tags to find locations
    # on each access is too expensive. This makes it complicated to base
    # LocationSource on Whitelist, so we don't and read the same XML here
    # instead.

    config_url = 'whitelist-url'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):

        zope.interface.implements(
            ILocationSource,
            zeit.cms.content.contentsource.IAutocompleteSource)

        def get_check_types(self):
            """IAutocompleteSource, but not applicable for us"""
            return []

        def __contains__(self, value):
            return True

    def getValues(self, context):
        xml = self._get_tree()
        return [
            unicode(node).strip() for node in xml.iterchildren('tag')
            if node.get('entity_type') == 'Location']

    def getTitle(self, context, value):
        return value

    def search(self, term):
        term = term.lower()
        return [x for x in self.getValues(None) if term in x.lower()]

locationSource = LocationSource()
