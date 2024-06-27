"""This module implements references between ICMSContent objects, where the
reference itself can have its own properties. These references are stored as
XML nodes::

    A ----------> B
       foo=bar

    C ----------> B
       foo=qux

Terminology note: the "source" (A or C) references the "target" (B).

"""
import copy
import urllib.parse

import grokcore.component as grok
import lxml.objectify
import z3c.traverser.interfaces
import zope.component
import zope.publisher.interfaces
import zope.security.proxy
import zope.traversing.browser.absoluteurl

from zeit.cms.content.util import create_parent_nodes
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces


class ReferenceProperty:
    """Property descriptor for tuples of IReference.

    The source object must provide ``IXMLRepresentation``, as the references
    are stored as XML nodes.
    """

    def __init__(self, path, xml_reference_name):
        """
        :param str path: an lxml ObjectPath where to store the XML nodes
        :param unicode xml_reference_name: type of IXMLReference to use

        For example, to store references of type "image" in <image> nodes
        contained within <head>::

          images = ReferenceProperty('.head.image', xml_reference_name='image')
        """
        self.path = lxml.objectify.ObjectPath(path)
        self.xml_reference_name = xml_reference_name

    def __get__(self, instance, class_):
        """Returns a specialized tuple of IReference objects.

        The tuple supports additional methods, most importantly
        ``create(target)`` to create an IReference object to the given
        ICMSContent (see class ``Reference`` for more details), which is needed
        for writing to a ReferenceProperty::

            source.myref = (source.myref.create(target)),)

        Even if the ReferenceProperty is empty, it returns a specialized empty
        tuple that supports ``create()``.
        """
        if instance is None:
            return self
        if not zeit.cms.content.interfaces.IXMLRepresentation.providedBy(instance):
            raise TypeError(
                'References descriptor can only be used on objects '
                'that provided IXMLRepresentation, not %s' % type(instance)
            )
        result = []
        attribute = self.__name__(instance)
        for element in self._reference_nodes(instance):
            reference = zope.component.queryMultiAdapter(
                (instance, element),
                zeit.cms.content.interfaces.IReference,
                name=self.xml_reference_name,
            )
            if reference is not None and reference.target is not None:
                reference.attribute = attribute
                reference.xml_reference_name = self.xml_reference_name
                result.append(reference)
        return References(
            result, source=instance, attribute=attribute, xml_reference_name=self.xml_reference_name
        )

    def __set__(self, instance, value):
        """Writes ``value`` into XML of ``instance``.

        :param value: an iterable of IReference objects (otherwise a
            ``TypeError`` is raised)

        This replaces all XML nodes, so if clients want to _change_ something,
        they need to take care to get the value, do the change, and write the
        whole value back -- otherwise, properties of the IReference objects
        will be lost.
        """
        self._check_for_references(value)
        value = self._filter_duplicates(value)
        xml = zope.security.proxy.getObject(instance.xml)
        value = tuple(zope.security.proxy.getObject(x.xml) for x in value)
        if str(self.path) == '.':  # Special case for single reference
            assert len(value) <= 1
            # XXX Kludge. What we actually want here is the idempotent
            # behaviour of ObjectPath.setattr, but that refuses to operate on
            # the root node. So we cheat and copy the target value in case it's
            # the same as the source value, and then empty the source
            # completely.
            if value:
                value = [copy.copy(value[0])]
            xml.attrib.clear()
            for child in xml.iterchildren():
                xml.remove(child)
            if value:
                value = value[0]
                for key, val in value.attrib.items():
                    xml.set(key, val)
                for child in value.iterchildren():
                    xml.append(copy.copy(child))
        else:
            for node in self._reference_nodes(instance):
                node.getparent().remove(node)
            parent, name = create_parent_nodes(self.path, xml)
            for node in value:
                node.tag = name
                parent.append(node)
            else:
                parent.text = None
        instance._p_changed = True

    def _check_for_references(self, values):
        """Raise ``TypeError`` if any value does not provide ``IReference``."""
        for value in values:
            if not zeit.cms.content.interfaces.IReference.providedBy(value):
                raise TypeError(
                    'Only accept IReference to avoid programming '
                    'errors that could lead to data loss.'
                )

    def _filter_duplicates(self, value):
        # set does not preserve order, so we use dict keys instead.
        result = {}
        for item in value:
            if item not in result:
                result[item] = True
        return result.keys()

    def __name__(self, instance):
        """Returns name of the schema field."""
        class_ = type(instance)
        for name in dir(class_):
            if getattr(class_, name, None) is self:
                return name
        return None

    def _reference_nodes(self, instance):
        xml = zope.security.proxy.getObject(instance.xml)
        if str(self.path) == '.':
            return [xml]
        node = self.path.find(xml, None)
        if node is None:
            return []
        return list(node.getparent().iterchildren(node.tag))

    @staticmethod
    def create_reference(source, attribute, target, xml_reference_name, suppress_errors=False):
        """Creates an IReference object.

        Not meant to be called directly, clients should use
        ``References.create()`` or ``IReference.create()`` (see ``__get__``).

        To create the IReference, ``target`` is adapted to
        ``IXMLReference`` and the result adapted to ``IReference``.

        ``suppress_errors`` is passed to ``IXMLReferenceUpdater``, it's not a
        generic "catch all exceptions" switch.
        """
        if zeit.cms.content.interfaces.IReference.providedBy(target):
            raise TypeError(
                'Cannot create reference for reference because it ' 'could lead to data loss.'
            )

        element = None
        if suppress_errors:
            try:
                element = zope.component.getAdapter(
                    target,
                    zeit.cms.content.interfaces.IXMLReference,
                    name=xml_reference_name + '_suppress_errors',
                )
            except zope.component.ComponentLookupError:
                pass
        if element is None:
            try:
                element = zope.component.getAdapter(
                    target, zeit.cms.content.interfaces.IXMLReference, name=xml_reference_name
                )
            except zope.component.ComponentLookupError:
                raise ValueError(
                    ("Could not create XML reference type '%s' for %s " '(referenced by %s).')
                    % (xml_reference_name, target.uniqueId, source.uniqueId)
                )
        reference = zope.component.queryMultiAdapter(
            (source, element), zeit.cms.content.interfaces.IReference, name=xml_reference_name
        )
        reference.attribute = attribute
        reference.xml_reference_name = xml_reference_name
        return reference

    @staticmethod
    def find_reference(source, attribute, target, default=None):
        if zeit.cms.interfaces.ICMSContent.providedBy(target):
            target = target.uniqueId
        result = None
        value = getattr(source, attribute, ())
        if not isinstance(value, tuple):
            # We must support both multi-valued and single-valued reference
            # properties here, since our clients cannot know which kind it is.
            value = (value,)
        for reference in value:
            if reference.target_unique_id == target:
                if result is not None:
                    raise ValueError(
                        '%s has more than one reference to %s on %s'
                        % (source.uniqueId, target, attribute)
                    )
                result = reference
        if result is not None:
            return result
        return default


class SingleReferenceProperty(ReferenceProperty):
    """Property descriptor for a single IReference.

    IReference (like the specialized tuple of ReferenceProperty) supports
    ``create(target)`` so clients can create references in the single-valued
    case as well::

        source.singleref = source.singleref.create(target)
    """

    def __get__(self, instance, class_):
        if instance is None:
            return self
        value = super().__get__(instance, class_)
        if value:
            return value[0]
        attribute = self.__name__(instance)
        return EmptyReference(instance, attribute, self.xml_reference_name)

    def __set__(self, instance, value):
        if value is None:
            value = ()
        else:
            value = (value,)
        super().__set__(instance, value)


class SingleResource(SingleReferenceProperty):
    """Property descriptor for a single ICMSContent object. Uses IReference
    internally, but hides this from clients.
    """

    def __get__(self, instance, class_):
        if instance is None:
            return self
        reference = super().__get__(instance, class_)
        return reference.target

    def __set__(self, instance, value):
        if value is not None:
            reference = super().__get__(instance, None)
            value = reference.create(value)
        super().__set__(instance, value)


class MultiResource(ReferenceProperty):
    """Property descriptor for a tuple of ICMSContent objects. Uses IReference
    internally, but hides this from clients.
    """

    def references(self, instance):
        return super().__get__(instance, None)

    def __get__(self, instance, class_):
        if instance is None:
            return self
        return tuple(x.target for x in self.references(instance))

    def __set__(self, instance, value):
        references = self.references(instance)
        # NOTE: You must not access the same XML nodes
        # via both ReferenceProperty and MultiResource,
        # since setting MultiResource overwrites existing Reference nodes,
        # thus destroying any properties they might have had.
        value = tuple(references.create(x) for x in value)
        super().__set__(instance, value)


@zope.interface.implementer(zeit.cms.content.interfaces.IReferences)
class References(tuple):
    def __new__(cls, items, source, attribute, xml_reference_name):
        self = super().__new__(cls, items)
        self.source = source
        self.attribute = attribute
        self.xml_reference_name = xml_reference_name
        return self

    def create(self, target, suppress_errors=False):
        """See ReferenceProperty.__get__"""
        return ReferenceProperty.create_reference(
            self.source, self.attribute, target, self.xml_reference_name, suppress_errors
        )

    def get(self, target, default=None):
        """Supports ICMSContent resolving for IReference."""
        return ReferenceProperty.find_reference(self.source, self.attribute, target, default)


@zope.interface.implementer(zeit.cms.content.interfaces.IReference)
class EmptyReference:
    """Helper so an empty SingleReferenceProperty still supports
    ``create()``.
    """

    target = None
    target_unique_id = None
    # XXX Do we need non-fake values for ILocation?
    __parent__ = None
    __name__ = None

    def __init__(self, source, attribute, xml_reference_name):
        self.source = source
        self.attribute = attribute
        self.xml_reference_name = xml_reference_name

    def create(self, target, suppress_errors=False):
        return ReferenceProperty.create_reference(
            self.source, self.attribute, target, self.xml_reference_name, suppress_errors
        )

    def get(self, target, default=None):
        return default

    def __bool__(self):
        return False

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return True
        return other is None


ID_PREFIX = 'reference://'


@grok.implementer(zeit.cms.content.interfaces.IReference)
class Reference(grok.MultiAdapter, zeit.cms.content.xmlsupport.Persistent):
    grok.adapts(zeit.cms.content.interfaces.IXMLRepresentation, zeit.cms.interfaces.IXMLElement)
    grok.baseclass()

    # XXX kludgy: These must be set manually after adapter call by clients.
    attribute = None
    xml_reference_name = None

    def __init__(self, context, element):
        self.xml = element
        # set parent last so we don't trigger a write
        self.__parent__ = context

    def __setattr__(self, key, value):
        # XXX the kludge around our attributes continues
        if key not in ['attribute', 'xml_reference_name'] and not key.startswith('_p_'):
            self._p_changed = True
        # skip immediate superclass since it has the bevaiour we want to change
        super(zeit.cms.content.xmlsupport.Persistent, self).__setattr__(key, value)

    @property
    def target_unique_id(self):
        return self.xml.get('href')

    @property
    def __name__(self):
        return self.target_unique_id

    @property
    def target(self):
        try:
            return zeit.cms.interfaces.ICMSContent(self.target_unique_id)
        except (TypeError, LookupError):
            return None

    def get(self, target, default=None):
        return ReferenceProperty.find_reference(self.__parent__, self.attribute, target, default)

    def create(self, target, suppress_errors=False):
        return ReferenceProperty.create_reference(
            self.__parent__, self.attribute, target, self.xml_reference_name, suppress_errors
        )

    def _update_target_unique_id(self):
        # Support renaming (see doc/implementation/move.txt).
        self.xml.set('href', self.target.uniqueId)

    @property
    def uniqueId(self):
        return '%s?%s' % (
            ID_PREFIX,
            urllib.parse.urlencode(
                {
                    'source': self.__parent__.uniqueId,
                    'attribute': self.attribute,
                    'target': self.target_unique_id,
                }
            ),
        )

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.__parent__.uniqueId == other.__parent__.uniqueId
            and self.attribute == other.attribute
            and self.target.uniqueId == other.target_unique_id
        )

    def __hash__(self):
        return hash((self.__parent__.uniqueId, self.attribute, self.target_unique_id))

    def __repr__(self):
        return '<%s.%s %s>' % (self.__class__.__module__, self.__class__.__name__, self.uniqueId)


@grok.adapter(str, name=ID_PREFIX)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_reference(unique_id):
    assert unique_id.startswith(ID_PREFIX)
    params = urllib.parse.parse_qs(urllib.parse.urlparse(unique_id).query)
    source = zeit.cms.cmscontent.resolve_wc_or_repository(params['source'][0])
    references = getattr(source, params['attribute'][0], {})
    return references.get(params['target'][0])


@zope.component.adapter(
    zeit.cms.content.interfaces.IReference, zeit.cms.browser.interfaces.ICMSLayer
)
class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    def __str__(self):
        base = zope.traversing.browser.absoluteURL(self.context.__parent__, self.request)
        return base + '/++attribute++%s/%s' % (
            # XXX zope.publisher seems to decode stuff (but why?), so we need
            # to encode twice
            self.context.attribute,
            urllib.parse.quote_plus(urllib.parse.quote_plus(self.context.__name__)),
        )


@zope.interface.implementer(z3c.traverser.interfaces.IPluggableTraverser)
class Traverser:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        reference = self.context.get(urllib.parse.unquote_plus(name))
        if reference is not None:
            return reference
        raise zope.publisher.interfaces.NotFound(self.context, name, request)


class OverridableProperty:
    """Descriptor that allows acessing an attribute either on the local
    instance or on an another object accessible from there.

    class MyReference:

        @property
        def target(self):
            return MyArticle()

        teaserText = OverridableProperty(
            ICommonMetadata['teaserText'], original='target')

        _teaserText_local = None

    The idea is that reading ``reference.teaserText`` first tries the "local"
    variant (an attribute that adheres to the naming convention
    ``_NAME_local``). If that is not present, it tries to read from the target
    object. If that doesn't work, we return the field's missing_value.

    Writing the property always writes to the "local" attribute.
    """

    def __init__(self, field, original):
        """Parameters:
        field: a zope.schema.Field, used for its name and missing_value
        original: the name on the instance under which we get the target object
        """
        self.field = field
        self.original = original

    def __get__(self, inst, cls):
        if inst is None:
            return self
        value = getattr(inst, '_%s_local' % self.field.__name__)
        original = getattr(inst, self.original)
        if value is not self.field.missing_value:
            return value
        elif original:
            return getattr(original, self.field.__name__)
        else:
            self.field.missing_value

    def __set__(self, inst, value):
        __traceback_info__ = (self.field.__name__, value)
        setattr(inst, '_%s_local' % self.field.__name__, value)
