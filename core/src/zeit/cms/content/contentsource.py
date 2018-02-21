import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.component
import zope.interface


class ICMSContentSource(zope.schema.interfaces.ISource):
    """A source for CMS content types."""


class INamedCMSContentSource(ICMSContentSource):
    """A source for CMS content which is registered as utility."""

    name = zope.interface.Attribute("Utility name of the source")

    def get_check_types():
        """Return a sequence of cms type identifiers which are included."""


class IAutocompleteSource(INamedCMSContentSource):
    """Marker that this source supports autocomplete."""


class CMSContentSource(object):
    """A source for all cms content."""

    zope.interface.implements(INamedCMSContentSource)

    name = 'all-types'
    check_interfaces = zeit.cms.interfaces.ICMSContentType

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
            assert issubclass(self.check_interfaces,
                              zope.interface.interfaces.IInterface)
            for name, interface in zope.component.getUtilitiesFor(
                    self.check_interfaces):
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
    check_interfaces = (
        zeit.cms.repository.interfaces.IFolder,)


folderSource = FolderSource()


class ChoicePropertyWithCMSContentSource(object):

    zope.component.adapts(
        zope.schema.interfaces.IChoice,
        ICMSContentSource,
        zope.interface.Interface)

    def __init__(self, context, source, content):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        if not value:
            return None
        content = zeit.cms.interfaces.ICMSContent(value, None)
        if content in self.source:
            return content

    def toProperty(self, value):
        return value.uniqueId
