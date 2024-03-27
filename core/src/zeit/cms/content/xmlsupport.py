from io import StringIO

import grokcore.component as grok
import lxml.etree
import persistent
import persistent.interfaces
import zope.interface
import zope.security.interfaces
import zope.security.proxy

from zeit.cms.workingcopy.interfaces import IWorkingcopy
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.lxmlpickle  # extended pickle support
import zeit.cms.interfaces
import zeit.cms.repository.repository
import zeit.connector.interfaces


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
class XMLRepresentationBase:
    #: XML string with which to initalize new objects. Define in subclass.
    default_template = None

    def __init__(self, xml_source=None):
        if xml_source is None:
            if self.default_template is None:
                raise NotImplementedError('default_template needs to be set in subclasses')
            xml_source = StringIO(self.default_template)
        self.xml = lxml.etree.parse(xml_source).getroot()


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLContent)
class XMLContentBase(
    zeit.cms.repository.repository.ContentBase, XMLRepresentationBase, persistent.Persistent
):
    """Base class for XML content."""


_default_marker = object()


class Persistent:
    """Helper to indicate changes for object modified xml trees."""

    def __setattr__(self, key, value):
        if not (key.startswith('_p_') or key.startswith('_v_')):
            self._p_changed = True
        super().__setattr__(key, value)

    @property
    def _p_changed(self):
        persistent = self.__get_persistent()
        return persistent._p_changed if persistent is not None else None

    @_p_changed.setter
    def _p_changed(self, value):
        persistent = self.__get_persistent()
        if persistent is not None:
            persistent._p_changed = value

    @property
    def _p_jar(self):
        persistent = self.__get_persistent()
        if persistent is not None:
            return persistent._p_jar
        return None

    def __get_persistent(self):
        parent = getattr(self, '__parent__', None)
        while parent is not None:
            unproxied = zope.proxy.removeAllProxies(parent)
            if persistent.interfaces.IPersistent.providedBy(unproxied):
                return unproxied
            parent = parent.__parent__


@zope.interface.implementer(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
class SynchronisingDAVPropertyToXMLEvent:
    vetoed = False

    def __init__(self, namespace, name, value):
        self.namespace, self.name, self.value = namespace, name, value

    def veto(self):
        self.vetoed = True


@grok.subscribe(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def veto_dav(event):
    if event.namespace == 'DAV:':
        event.veto()


@grok.subscribe(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def veto_internal(event):
    if event.namespace == zeit.connector.interfaces.INTERNAL_PROPERTY:
        event.veto()


@zope.component.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser)
class PropertyToXMLAttribute:
    """Attribute nodes reside in the head."""

    def __init__(self, context):
        self.context = context
        self.properties = dict(zeit.connector.interfaces.IWebDAVProperties(context))

        # Now get the current live-properties
        repository = zope.component.queryUtility(zeit.cms.repository.interfaces.IRepository)
        if repository is not None and context.uniqueId:
            try:
                repository_content = repository.getContent(context.uniqueId)
            except KeyError:
                pass
            else:
                live_properties = zeit.connector.interfaces.IWebDAVProperties(repository_content)
                for key, value in live_properties.items():
                    if not live_properties.is_writeable_on_checkin(*key):
                        self.properties[key] = value

    def set(self, namespace, name, value=_default_marker):
        self.delAttribute(namespace, name)
        if value is _default_marker:
            value = self.properties[(name, namespace)]
        if value is not zeit.connector.interfaces.DeleteProperty:
            self.addAttribute(namespace, name, value)

    def sync(self):
        # Remove all properties in xml first
        for node in self.context.xml.xpath('//head/attribute'):
            node.getparent().remove(node)

        # Now, set each property to xml, sort them to get a consistent xml
        for (name, namespace), value in sorted(self.properties.items()):
            if value is zeit.connector.interfaces.DeleteProperty:
                continue
            self.addAttribute(namespace, name, value)

    def addAttribute(self, namespace, name, value):
        sync_event = SynchronisingDAVPropertyToXMLEvent(namespace, name, value)
        zope.event.notify(sync_event)
        if sync_event.vetoed:
            return
        head = self.context.xml.find('head')
        if head is None:
            head = lxml.builder.E.head()
            self.context.xml.append(head)
        head.append(lxml.builder.E.attribute(value, ns=namespace, name=name))

    def delAttribute(self, namespace, name):
        root = self.context.xml
        xpath = '//head/attribute[@ns="%s" and @name="%s"]' % (namespace, name)
        for node in root.xpath(xpath):
            parent = node.getparent()
            parent.remove(node)


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent,
)
def map_dav_property_to_xml(context, event):
    """Copy dav properties to XML if possible."""
    # Checking ILocalContent.providedBy(context) would be semantically nicer,
    # but then we would not support the "AddForm and checkin directly" usecase
    # that most content types (except for Article) use.
    parent = context.__parent__
    if parent is not None and not IWorkingcopy.providedBy(parent):
        return
    # Remove security proxy: If the user was allowed to change the property
    # (via setattr) *we* copy that to the xml, regardles of the security.
    content = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.IXMLRepresentation(context)
    )
    sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
    sync.set(event.property_namespace, event.property_name, event.new_value)


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent,
)
def map_dav_properties_to_xml_before_checkin(context, event):
    """Copy over all DAV properties to the xml before checkin."""
    content = zope.security.proxy.removeSecurityProxy(
        zeit.cms.content.interfaces.IXMLRepresentation(context)
    )
    sync = zeit.cms.content.interfaces.IDAVPropertyXMLSynchroniser(content)
    sync.sync()


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReferenceUpdater)
class XMLReferenceUpdater:
    target_iface = None
    suppress_errors = False

    def __init__(self, context):
        self.context = context

    def update(self, xml_node, suppress_errors=False):
        """Only run the real update if context is adaptable to target_iface.

        Subclasses need to set the target_iface attribute and implement
        update_with_context(xml_node, context) in order to use this feature.

        """
        __traceback_info__ = (self.context.uniqueId,)
        context = self.target_iface(self.context, None)
        if context is None:
            return None
        # XXX It would be cleaner to pass suppress_errors as a parameter to
        # update_with_context, but then all subclasses would need to be changed
        # to offer the new signature.
        self.suppress_errors = suppress_errors
        return self.update_with_context(xml_node, context)


class XMLReferenceUpdaterRunner(XMLReferenceUpdater):
    """Adapter that updates metadata etc on an XML reference."""

    def update(self, xml_node, suppress_errors=False):
        """Update xml_node with data from the content object."""
        for name, updater in sorted(
            zope.component.getAdapters(
                (self.context,), zeit.cms.content.interfaces.IXMLReferenceUpdater
            )
        ):
            if not name:
                # The unnamed adapter is the one which runs all the named
                # adapters, i.e. this one.
                continue
            updater.update(xml_node, suppress_errors)


class CommonMetadataUpdater(XMLReferenceUpdater):
    """Put information for ICommonMetadata into the channel."""

    target_iface = zeit.cms.content.interfaces.ICommonMetadata

    def update_with_context(self, entry, metadata):
        update_child_node(entry, 'supertitle', metadata.teaserSupertitle or metadata.supertitle)
        update_child_node(entry, 'title', metadata.teaserTitle)
        update_child_node(entry, 'text', metadata.teaserText)
        update_child_node(entry, 'description', metadata.teaserText)
        update_child_node(entry, 'byline', metadata.byline)
        if metadata.year:
            entry.set('year', str(metadata.year))
        if metadata.volume:
            entry.set('issue', str(metadata.volume))
        if metadata.ressort:
            entry.set('ressort', str(metadata.ressort))
        if metadata.serie:
            entry.set('serie', str(metadata.serie.serienname))
        try:
            type_decl = zeit.cms.interfaces.ITypeDeclaration(self.context)
        except TypeError:
            return
        if type_decl.type_identifier:
            entry.set('contenttype', str(type_decl.type_identifier))


def update_child_node(parent, name, text):
    node = parent.find(name)
    if node is None:
        node = lxml.etree.Element(name)
        parent.append(node)
    node.text = text
