# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

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

    def __init__(self, path, xml_reference_name):
        self.path = lxml.objectify.ObjectPath(path)
        self.xml_reference_name = xml_reference_name

    def __get__(self, instance, class_):
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
                result.append(reference)
        return References(
            result, source=instance, attribute=attribute,
            xml_reference_name=self.xml_reference_name)

    def __set__(self, instance, value):
        xml = zope.security.proxy.getObject(instance.xml)
        value = tuple(zope.security.proxy.getObject(x.xml) for x in value)
        self.path.setattr(xml, value)
        instance._p_changed = True

    def __name__(self, instance):
        class_ = type(instance)
        for name in dir(class_):
            if getattr(class_, name, None) is self:
                return name

    def _reference_nodes(self, instance):
        try:
            return self.path.find(zope.security.proxy.getObject(instance.xml))
        except AttributeError:
            return []

    def update_metadata(self, instance):
        for reference in self.__get__(instance, None):
            reference.update_metadata()


class MultiResource(ReferenceProperty):

    def references(self, instance):
        return super(MultiResource, self).__get__(instance, None)

    def __get__(self, instance, class_):
        if instance is None:
            return self
        return tuple(x.target for x in self.references(instance))

    def __set__(self, instance, value):
        references = self.references(instance)
        value = tuple(references.get(x) or references.create(x) for x in value)
        super(MultiResource, self).__set__(instance, value)
        self.update_metadata(instance)

    def update_metadata(self, instance):
        for reference in self.references(instance):
            reference.update_metadata()


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

    def create(self, target):
        try:
            element = zope.component.getAdapter(
                target, zeit.cms.content.interfaces.IXMLReference,
                name=self.xml_reference_name)
        except zope.component.ComponentLookupError:
            raise ValueError(
                ("Could not create XML reference type '%s' for %s "
                 "(referenced by %s).") % (
                self.xml_reference_name,
                target.uniqueId, self.source.uniqueId))
        reference = zope.component.queryMultiAdapter(
            (self.source, element), zeit.cms.content.interfaces.IReference,
            name=self.xml_reference_name)
        reference.attribute = self.attribute
        return reference

    def get(self, target, default=None):
        if zeit.cms.interfaces.ICMSContent.providedBy(target):
            target = target.uniqueId
        result = None
        for reference in self:
            if reference.target_unique_id == target:
                if result is not None:
                    raise ValueError(
                        '%s has more than one reference to %s on %s' %
                        (self.source.uniqueId, target, self.attribute))
                result = reference
        if result is not None:
            return result
        return default


ID_PREFIX = 'reference://'


class Reference(grok.MultiAdapter, zeit.cms.content.xmlsupport.Persistent):

    grok.adapts(
        zeit.cms.content.interfaces.IXMLRepresentation,
        gocept.lxml.interfaces.IObjectified)
    grok.implements(zeit.cms.content.interfaces.IReference)
    grok.baseclass()

    attribute = None  # XXX must be set after adapter call by client

    def __init__(self, context, element):
        self.xml = element
        # set parent last so we don't trigger a write
        self.__parent__ = context

    @property
    def target_unique_id(self):
        return self.xml.get('href')

    @property
    def __name__(self):
        return self.target_unique_id

    @property
    def target(self):
        return zeit.cms.interfaces.ICMSContent(self.target_unique_id, None)

    def update_metadata(self):
        if self.target is None:
            return
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(self.target)
        updater.update(self.xml)
        self._p_changed = True

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
