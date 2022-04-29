import grokcore.component as grok
import logging
import lxml.etree
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.util
import zeit.connector.interfaces
import zeit.connector.resource
import zope.container.contained
import zope.interface
import zope.proxy
import zope.schema


log = logging.getLogger(__name__)
# Marker object to indicate no add form.
SKIP_ADD = object()


_provides_dav_property = zeit.cms.content.dav.DAVProperty(
    zope.schema.Object(zope.interface.Interface),
    'http://namespaces.zeit.de/CMS/meta', 'provides', 'provides')


class TypeDeclaration:

    interface = None
    interface_type = zeit.cms.interfaces.ICMSContentType

    # The "type" in DAV. If given the class will also implement IDAVContent
    type = None
    factory = NotImplemented
    title = None
    addform = None
    addpermission = None
    register_as_type = True

    def __init__(self):
        if self.addform is None:
            package = '.'.join(self.__module__.split('.')[:-1])
            self.addform = package + '.Add'

    def content(self, resource):
        raise NotImplementedError

    def resource_body(self, content):
        raise NotImplementedError

    def resource_content_type(self, content):
        return None

    def resource_properties(self, content):
        try:
            return zeit.connector.interfaces.IWebDAVReadProperties(content)
        except TypeError:
            return zeit.connector.resource.WebDAVProperties()

    def resource(self, content):
        self._serialize_provided_interfaces_to_dav(content)
        return zeit.connector.resource.Resource(
            content.uniqueId, content.__name__, self.type,
            data=self.resource_body(content),
            contentType=self.resource_content_type(content),
            properties=self.resource_properties(content))

    # Serializing/deserializing provided interfaces is independent of the
    # content type. For the content->resource adapter, the functionality is
    # integrated (via the AfterObjectConstructedEvent) into the generic
    # adapter.
    # But for the resource->content direction there is no fallback case, so
    # there is no generic adapter for this direction. Thus, there is no generic
    # place to integrate the "provides" functionality. That's why it is
    # included in the "concrete" adapter; however, since this adapter is in
    # fact the only implementation in the whole system, and the possibility of
    # overriding it for a content type is purely theoretical at this point, we
    # can get away with it.
    def _serialize_provided_interfaces_to_dav(self, obj):
        # Remove all proxies to not get any implements from proxies
        unwrapped = zope.proxy.removeAllProxies(obj)
        # Dear Zope, why is ContainedProxy not a zope.proxy?
        unwrapped = zope.container.contained.getProxiedObject(unwrapped)
        # We don't want to store ILocalContent of course since we're about to
        # add to the repository. (Unfortunately, __provides__ is a custom type
        # and not a simple list, so we can only manipulate it through the
        # zope.interface functions, which is a little clumsy.)
        try:
            zope.interface.noLongerProvides(
                unwrapped, zeit.cms.workingcopy.interfaces.ILocalContent)
        except ValueError:
            # Can only remove directly provided interfaces.
            removed_local_content = False
        else:
            removed_local_content = True
        provides = unwrapped.__provides__
        if not list(zope.interface.directlyProvidedBy(unwrapped)):
            # In the case we don't have any direct provides just store nothing.
            provides = None
        try:
            _provides_dav_property.__set__(unwrapped, provides)
        except zope.security.interfaces.Forbidden:
            # We probably stored an object providing IRepositoryContent,
            # thus we may not change anything.
            pass
        if removed_local_content:
            zope.interface.alsoProvides(
                unwrapped, zeit.cms.workingcopy.interfaces.ILocalContent)

    @property
    def type_identifier(self):
        if self.type is not None:
            return self.type
        assert self.interface is not None
        return u'%s.%s' % (self.interface.__module__, self.interface.__name__)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.repository.interfaces.IAfterObjectConstructedEvent)
def restore_provided_interfaces_from_dav(obj, event):
    properties = event.resource.properties
    new_provides = _provides_dav_property.__get__(obj, obj.__class__,
                                                  properties)
    if (new_provides is not None and
            new_provides != getattr(obj, '__provides__', None)):
        obj.__provides__ = new_provides
        # directly provide Interface to restore the _cls on __provides__
        zope.interface.alsoProvides(obj, zope.interface.Interface)


class XMLContentTypeDeclaration(TypeDeclaration):

    def content(self, resource):
        try:
            return self.factory(xml_source=resource.data)
        except lxml.etree.XMLSyntaxError as e:
            log.warning("Could not parse XML of %s: %s (%s)" % (
                resource.id, e.__class__.__name__, e))
            return None

    def resource_body(self, content):
        return zeit.cms.util.MemoryFile(
            zeit.cms.content.interfaces.IXMLSource(content))

    def resource_content_type(self, content):
        return 'text/xml'


def get_type(content):
    for interface in zope.interface.providedBy(content):
        try:
            return interface.getTaggedValue('zeit.cms.type')
        except KeyError:
            continue
    return None
