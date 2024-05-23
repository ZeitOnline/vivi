from io import StringIO

import lxml.etree
import persistent
import persistent.interfaces
import zope.interface
import zope.security.interfaces
import zope.security.proxy

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
