import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.connector.resource


class ICMSContentSource(zope.schema.interfaces.ISource):
    """A source for CMS content types."""


class INamedCMSContentSource(ICMSContentSource):
    """A source for CMS content which is registered as utility."""

    name = zope.interface.Attribute('Utility name of the source')

    def get_check_types():
        """Return a sequence of cms type identifiers which are included."""


class IAutocompleteSource(INamedCMSContentSource):
    """Marker that this source supports autocomplete."""

    # Coupling us to zeit.find here is not great, but I don't see a helpful way
    # to handle this in a more abstract manner.
    additional_query_conditions = zope.interface.Attribute(
        'Optional: additional kwargs for zeit.find.search.query'
    )


@zope.interface.implementer(INamedCMSContentSource)
class CMSContentSource:
    """A source for all cms content."""

    name = 'all-types'
    check_interfaces = zeit.cms.interfaces.ICMSContentType

    def __init__(self, check_interfaces=None):
        if check_interfaces is not None:
            self.check_interfaces = check_interfaces

    def __contains__(self, value):
        if not self.verify_interface(value):
            return False

        # Interface is correct, make sure the object actually available
        content = zeit.cms.interfaces.ICMSContent(value.uniqueId, None)
        return content is not None

    def get_check_interfaces(self):
        check = []
        if isinstance(self.check_interfaces, tuple):
            check.extend(self.check_interfaces)
        else:
            assert issubclass(self.check_interfaces, zope.interface.interfaces.IInterface)
            for _name, interface in zope.component.getUtilitiesFor(self.check_interfaces):
                check.append(interface)
        return check

    def get_check_types(self):
        types = []
        for interface in self.get_check_interfaces():
            __traceback_info__ = (interface,)
            types.append(interface.getTaggedValue('zeit.cms.type'))
        return types

    def verify_interface(self, value):
        for interface in self.get_check_interfaces():
            if interface.providedBy(value):
                return True
        return False


cmsContentSource = CMSContentSource()


class FolderSource(CMSContentSource):
    """A source containing folders."""

    name = 'folders'
    check_interfaces = (zeit.cms.repository.interfaces.IFolder,)


folderSource = FolderSource()


@zope.component.adapter(
    zope.schema.interfaces.IChoice,
    ICMSContentSource,
    zope.interface.Interface,
    zeit.connector.resource.PropertyKey,
)
class ChoicePropertyWithCMSContentSource:
    def __init__(self, context, source, properties, propertykey):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        if not value:
            return None
        content = zeit.cms.interfaces.ICMSContent(value, None)
        if content in self.source:
            return content
        return None

    def toProperty(self, value):
        return value.uniqueId
