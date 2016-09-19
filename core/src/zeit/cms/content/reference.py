"""This module implements references between ICMSContent objects, where the
reference itself can have its own properties. These references are stored as
XML nodes::

    A ----------> B
       foo=bar

    C ----------> B
       foo=qux

Terminology note: the "source" (A or C) references the "target" (B).

"""
import collections
import copy
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.objectify
import urllib
import urlparse
import z3c.traverser.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zope.component
import zope.publisher.interfaces
import zope.security.proxy
import zope.traversing.browser.absoluteurl


class ReferenceProperty(object):
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

        The metadata copied into the XML nodes is updated via
        IXMLReferenceUpdater on checkin.
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
        if not zeit.cms.content.interfaces.IXMLRepresentation.providedBy(
                instance):
            raise TypeError(
                'References descriptor can only be used on objects '
                'that provided IXMLRepresentation, not %s' % type(instance))
        result = []
        attribute = self.__name__(instance)
        for element in self._reference_nodes(instance):
            reference = zope.component.queryMultiAdapter(
                (instance, element), zeit.cms.content.interfaces.IReference,
                name=self.xml_reference_name)
            if reference is not None and reference.target is not None:
                reference.attribute = attribute
                reference.xml_reference_name = self.xml_reference_name
                result.append(reference)
        return References(
            result, source=instance, attribute=attribute,
            xml_reference_name=self.xml_reference_name)

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
            self.path.setattr(xml, value)
        instance._p_changed = True

    def _check_for_references(self, values):
        """Raise ``TypeError`` if any value does not provide ``IReference``."""
        for value in values:
            if not zeit.cms.content.interfaces.IReference.providedBy(value):
                raise TypeError('Only accept IReference to avoid programming '
                                'errors that could lead to data loss.')

    def _filter_duplicates(self, value):
        # We actually want an OrderedSet, so we use only the keys.
        result = collections.OrderedDict()
        for item in value:
            if item not in result.keys():
                result[item] = True
        return result.keys()

    def __name__(self, instance):
        """Returns name of the schema field."""
        class_ = type(instance)
        for name in dir(class_):
            if getattr(class_, name, None) is self:
                return name

    def _reference_nodes(self, instance):
        try:
            return self.path.find(zope.security.proxy.getObject(instance.xml))
        except AttributeError:
            return []

    def update_metadata(self, instance, suppress_errors=False):
        for reference in self.__get__(instance, None):
            reference.update_metadata(suppress_errors)

    @staticmethod
    def create_reference(
            source, attribute, target, xml_reference_name,
            suppress_errors=False):
        """Creates an IReference object.

        Not meant to be called directly, clients should use
        ``References.create()`` or ``IReference.create()`` (see ``__get__``).

        To create the IReference, ``target`` is adapted to
        ``IXMLReference`` and the result adapted to ``IReference``.

        ``suppress_errors`` is passed to ``IXMLReferenceUpdater``, it's not a
        generic "catch all exceptions" switch.
        """
        if zeit.cms.content.interfaces.IReference.providedBy(target):
            raise TypeError('Cannot create reference for reference because it '
                            'could lead to data loss.')

        element = None
        if suppress_errors:
            try:
                element = zope.component.getAdapter(
                    target, zeit.cms.content.interfaces.IXMLReference,
                    name=xml_reference_name + '_suppress_errors')
            except zope.component.ComponentLookupError:
                pass
        if element is None:
            try:
                element = zope.component.getAdapter(
                    target, zeit.cms.content.interfaces.IXMLReference,
                    name=xml_reference_name)
            except zope.component.ComponentLookupError:
                raise ValueError(
                    ("Could not create XML reference type '%s' for %s "
                     "(referenced by %s).") % (
                         xml_reference_name, target.uniqueId, source.uniqueId))
        reference = zope.component.queryMultiAdapter(
            (source, element), zeit.cms.content.interfaces.IReference,
            name=xml_reference_name)
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
                        '%s has more than one reference to %s on %s' %
                        (source.uniqueId, target, attribute))
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
        value = super(SingleReferenceProperty, self).__get__(instance, class_)
        if value:
            return value[0]
        attribute = self.__name__(instance)
        return EmptyReference(instance, attribute, self.xml_reference_name)

    def __set__(self, instance, value):
        if value is None:
            value = ()
        else:
            value = (value,)
        super(SingleReferenceProperty, self).__set__(instance, value)

    def _reference_nodes(self, instance):
        result = super(SingleReferenceProperty, self)._reference_nodes(
            instance)
        if not isinstance(result, list):
            result = [result]
        return result

    def update_metadata(self, instance, suppress_errors=False):
        reference = self.__get__(instance, None)
        if reference:
            reference.update_metadata(suppress_errors)


class SingleResource(SingleReferenceProperty):
    """Property descriptor for a single ICMSContent object. Uses IReference
    internally, but hides this from clients.
    """

    def __get__(self, instance, class_):
        if instance is None:
            return self
        reference = super(SingleResource, self).__get__(instance, class_)
        return reference.target

    def __set__(self, instance, value):
        if value is not None:
            reference = super(SingleResource, self).__get__(instance, None)
            value = reference.create(value)
        super(SingleResource, self).__set__(instance, value)
        self.update_metadata(instance)

    def update_metadata(self, instance, suppress_errors=False):
        reference = super(SingleResource, self).__get__(instance, None)
        if reference:
            reference.update_metadata(suppress_errors)


class MultiResource(ReferenceProperty):
    """Property descriptor for a tuple of ICMSContent objects. Uses IReference
    internally, but hides this from clients.
    """

    def references(self, instance):
        return super(MultiResource, self).__get__(instance, None)

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
        super(MultiResource, self).__set__(instance, value)
        self.update_metadata(instance)

    def update_metadata(self, instance, suppress_errors=False):
        for reference in self.references(instance):
            reference.update_metadata(suppress_errors)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_metadata_on_checkin(context, event):
    for name in dir(type(context)):
        # other descriptors might not support reading them from the class,
        # but the one that we want does.
        attr = getattr(type(context), name, None)
        if isinstance(attr, ReferenceProperty):
            attr.update_metadata(context)


class References(tuple):

    zope.interface.implements(zeit.cms.content.interfaces.IReferences)

    def __new__(cls, items, source, attribute, xml_reference_name):
        self = super(References, cls).__new__(cls, items)
        self.source = source
        self.attribute = attribute
        self.xml_reference_name = xml_reference_name
        return self

    def create(self, target, suppress_errors=False):
        """See ReferenceProperty.__get__"""
        return ReferenceProperty.create_reference(
            self.source, self.attribute, target, self.xml_reference_name,
            suppress_errors)

    def get(self, target, default=None):
        """Supports ICMSContent resolving for IReference."""
        return ReferenceProperty.find_reference(
            self.source, self.attribute, target, default)


class EmptyReference(object):
    """Helper so an empty SingleReferenceProperty still supports
    ``create()``.
    """

    zope.interface.implements(zeit.cms.content.interfaces.IReference)

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
            self.source, self.attribute, target, self.xml_reference_name,
            suppress_errors)

    def get(self, target, default=None):
        return default

    def __nonzero__(self):
        return False

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return True
        return other is None


ID_PREFIX = 'reference://'


class Reference(grok.MultiAdapter, zeit.cms.content.xmlsupport.Persistent):

    grok.adapts(
        zeit.cms.content.interfaces.IXMLRepresentation,
        gocept.lxml.interfaces.IObjectified)
    grok.implements(zeit.cms.content.interfaces.IReference)
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
        if (key not in ['attribute', 'xml_reference_name']
            and not key.startswith('_p_')):
            self._p_changed = True
        # skip immediate superclass since it has the bevaiour we want to change
        super(zeit.cms.content.xmlsupport.Persistent, self).__setattr__(
            key, value)

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
        return ReferenceProperty.find_reference(
            self.__parent__, self.attribute, target, default)

    def create(self, target, suppress_errors=False):
        return ReferenceProperty.create_reference(
            self.__parent__, self.attribute, target, self.xml_reference_name,
            suppress_errors)

    def update_metadata(self, suppress_errors=False):
        if self.target is None:
            return
        self._update_target_unique_id()
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(self.target)
        updater.update(self.xml, suppress_errors)
        self._p_changed = True

    def _update_target_unique_id(self):
        # Support renaming (see doc/implementation/move.txt).
        self.xml.set('href', self.target.uniqueId)

    @property
    def uniqueId(self):
        return '%s?%s' % (ID_PREFIX, urllib.urlencode(dict(
            source=self.__parent__.uniqueId, attribute=self.attribute,
            target=self.target_unique_id)))

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.__parent__.uniqueId == other.__parent__.uniqueId
                and self.attribute == other.attribute
                and self.target.uniqueId == other.target_unique_id)

    def __repr__(self):
        return '<%s.%s %s>' % (
            self.__class__.__module__, self.__class__.__name__, self.uniqueId)


@grok.adapter(basestring, name=ID_PREFIX)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_reference(unique_id):
    assert unique_id.startswith(ID_PREFIX)
    params = urlparse.parse_qs(urlparse.urlparse(unique_id).query)
    source = zeit.cms.cmscontent.resolve_wc_or_repository(params['source'][0])
    references = getattr(source, params['attribute'][0], {})
    return references.get(params['target'][0])


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    zope.component.adapts(
        zeit.cms.content.interfaces.IReference,
        zeit.cms.browser.interfaces.ICMSLayer)

    def __str__(self):
        base = zope.traversing.browser.absoluteURL(
            self.context.__parent__, self.request)
        return base + '/++attribute++%s/%s' % (
            # XXX zope.publisher seems to decode stuff (but why?), so we need
            # to encode twice
            self.context.attribute, urllib.quote_plus(
                urllib.quote_plus(self.context.__name__)))


class Traverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        reference = self.context.get(urllib.unquote_plus(name))
        if reference is not None:
            return reference
        raise zope.publisher.interfaces.NotFound(self.context, name, request)
