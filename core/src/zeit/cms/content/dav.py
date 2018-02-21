from zeit.cms.content.interfaces import WRITEABLE_ON_CHECKIN
import datetime
import grokcore.component
import logging
import lxml.etree
import pytz
import re
import sys
import time
import zc.iso8601.parse
import zeit.cms.content.interfaces
import zeit.cms.content.liveproperty
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zeit.connector.interfaces
import zope.app.security.interfaces
import zope.component
import zope.event
import zope.proxy
import zope.schema.interfaces
import zope.security.adapter
import zope.security.proxy
import zope.xmlpickle


logger = logging.getLogger(__name__)
PROPERTY_REGISTRY = {}


class DAVProperty(object):
    """WebDAV properties."""

    def __init__(self, field, namespace, name, use_default=False,
                 writeable=WRITEABLE_ON_CHECKIN):
        self.field = field
        self.namespace = namespace
        self.name = name
        if use_default:
            self.missing_value = field.default
        else:
            self.missing_value = field.missing_value
        # We cannot use a getUtility here, because this happens on import
        # time. We haven't got CA then.
        (zeit.cms.content.liveproperty.LiveProperties
         .register_live_property(name, namespace, writeable))
        PROPERTY_REGISTRY[(name, namespace)] = self

    def __get__(self, instance, class_, properties=None):
        __traceback_info = (instance, )
        if instance is None:
            return self
        if properties is None:
            properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        dav_value = properties.get((self.name, self.namespace),
                                   zeit.connector.interfaces.DeleteProperty)

        if (zope.proxy.removeAllProxies(dav_value) is
                zeit.connector.interfaces.DeleteProperty):
            value = self.missing_value
        else:
            field = self.field.bind(instance)
            __traceback_info__ = (instance, field,
                                  field.__name__, dav_value)
            try:
                value = zeit.cms.content.interfaces.IDAVPropertyConverter(
                    field).fromProperty(dav_value)
            except (ValueError, zope.schema.ValidationError), e:
                value = self.field.default
                if zeit.cms.interfaces.ICMSContent.providedBy(instance):
                    unique_id = instance.uniqueId
                else:
                    unique_id = repr(instance)
                logger.warning(
                    "Could not parse DAV property value %r for "
                    "%s.%s at %s [%s: %r]. Using default %r instead." % (
                        dav_value, instance.__class__.__name__, self.name,
                        unique_id, e.__class__.__name__, e.args, value))

        return value

    def __set__(self, instance, value):
        """Set the value to webdav properties."""
        read_properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        old_value = read_properties.get((self.name, self.namespace))
        if value is None:
            dav_value = zeit.connector.interfaces.DeleteProperty
        else:
            field = self.field.bind(instance)
            dav_value = zeit.cms.content.interfaces.IDAVPropertyConverter(
                field).toProperty(value)

        write_properties = zeit.cms.interfaces.IWebDAVWriteProperties(instance)
        write_properties[(self.name, self.namespace)] = dav_value

        zope.event.notify(zeit.cms.content.interfaces.DAVPropertyChangedEvent(
            instance, self.namespace, self.name, old_value, dav_value,
            self.field))


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def notify_cms_content_property_change(context, event):
    """Notify ICMSContent object about a property change.

    When a content object is adapted to extend functionality it is common to
    have an adapter to IWebDAVProperties from the adapter. In this case the
    orgiginal object would not be notified about changes.

    """
    if zeit.cms.interfaces.ICMSContent.providedBy(context):
        return
    # Get the CMSContent belonging to the properties
    properties = zeit.connector.interfaces.IWebDAVProperties(context)
    content = zeit.cms.interfaces.ICMSContent(properties, None)
    if content is None:
        return
    zope.event.notify(
        zeit.cms.content.interfaces.DAVPropertyChangedEvent(
            content, event.property_namespace, event.property_name,
            event.old_value, event.new_value,
            event.field))


class UnicodeProperty(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IGenericDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IFromUnicode)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        # Convert to unicode. We need to do that because lxml puts out an
        # ascii-str when the value has only 7bit characters. While this is an
        # optimisation in lxml we *need* a unicode here. If the value contains
        # 8 bit chars this is supposed to break.
        value = unicode(value)
        return self.context.fromUnicode(value)

    def toProperty(self, value):
        return unicode(value)


@zope.component.adapter(zope.schema.interfaces.IChoice)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
def ChoiceProperty(context):
    return zope.component.getMultiAdapter(
        (context, context.vocabulary),
        zeit.cms.content.interfaces.IDAVPropertyConverter)


class ChoicePropertyWithIterableSource(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IChoice,
                          zope.schema.interfaces.IIterableSource)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        for possible_value in self.source:
            if zeit.cms.content.interfaces.IDAVToken(possible_value) == value:
                return possible_value
        return value
        # XXX what to do here?
        raise ValueError(value)

    def toProperty(self, value):
        return zeit.cms.content.interfaces.IDAVToken(value)


class ChoicePropertyWithPrincipalSource(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IChoice,
                          zope.app.security.interfaces.IPrincipalSource)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        if value in self.source:
            return unicode(value)
        raise ValueError(value)

    def toProperty(self, value):
        return unicode(value)


DUMMY_REQUEST = zope.publisher.browser.TestRequest()


class ChoicePropertyWithObjectSource(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IChoice,
                          zeit.cms.content.sources.IObjectSource)

    def __init__(self, context, source):
        self.context = context
        self.source = source

    @property
    def terms(self):
        return zope.component.getMultiAdapter(
            (self.source, DUMMY_REQUEST), zope.browser.interfaces.ITerms)

    def fromProperty(self, value):
        # XXX We should think about using the token mechanism for all sources,
        # but we would need to generate a special (non-browser) token for this
        # purpose, since the default token is base64 encoded.
        try:
            return self.terms.getValue(value)
        except KeyError:
            # XXX Should we raise instead?
            return None

    def toProperty(self, value):
        return self.terms.getTerm(value).token


class ChoicePropertyWithIterableVocabulary(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IChoice,
                          zope.schema.interfaces.IIterableVocabulary)

    def __init__(self, context, vocabulary):
        self.context = context
        self.vocabulary = vocabulary

    def fromProperty(self, value):
        for term in self.vocabulary:
            if term.token == value:
                return term.value
        raise ValueError(value)

    def toProperty(self, value):
        for term in self.vocabulary:
            if term.value == value:
                return term.token
        raise ValueError(value)


class BoolProperty(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IBool)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        if value.lower() in ('yes', 'true'):
            return True
        return False

    def toProperty(self, value):
        if value:
            return 'yes'
        return 'no'


class DatetimeProperty(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IDatetime)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        if not value:
            return None
        try:
            return zc.iso8601.parse.datetimetz(value)
        except ValueError:
            pass
        try:
            # Uff. Try the "Thu, 13 Mar 2008 13:48:37 GMT" format
            date = datetime.datetime(*(time.strptime(
                value, '%a, %d %b %Y %H:%M:%S GMT')[0:6]))
        except ValueError:
            pass
        else:
            return date.replace(tzinfo=pytz.UTC)
        raise ValueError(value)

    def toProperty(self, value):
        if value is None:
            return u''
        if value.tzinfo is None:
            raise ValueError('%r has no timezone information' % value)
        return value.isoformat()


class DateProperty(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IDate)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        if not value:
            return None
        return datetime.date(*(time.strptime(value, '%Y-%m-%d')[0:3]))

    def toProperty(self, value):
        if value is None:
            return u''
        return value.isoformat()


@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
@zope.component.adapter(zope.schema.interfaces.ICollection)
def CollectionProperty(context):
    return zope.component.queryMultiAdapter(
        (context, context.value_type),
        zeit.cms.content.interfaces.IDAVPropertyConverter)


class CollectionTextLineProperty(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.ICollection,
                          zope.schema.interfaces.ITextLine)

    SPLIT_PATTERN = re.compile(r'(?!\\);')

    def __init__(self, context, value_type):
        self.context = context
        self.value_type = value_type
        self._type = context._type
        if isinstance(self._type, tuple):
            # XXX this is way hacky
            self._type = self._type[0]

    def fromProperty(self, value):
        from_prop = zeit.cms.content.interfaces.IDAVPropertyConverter(
            self.value_type)
        result = []
        start = 0
        while value:
            found = value.find(';', start)
            if found > 0 and value[found - 1] == '\\':
                start = found + 1
                continue
            if found > 0:
                item = value[:found]
                value = value[found + 1:]
            else:
                item = value
                value = ''
            item = item.replace('\\;', ';').replace('\\\\', '\\')
            item = from_prop.fromProperty(item)
            result.append(item)

        return self._type(result)

    def toProperty(self, value):
        to_prop = zeit.cms.content.interfaces.IDAVPropertyConverter(
            self.value_type)
        result = []
        for item in value:
            item = to_prop.toProperty(item)
            result.append(item.replace('\\', '\\\\').replace(';', '\\;'))
        return ';'.join(result)


class GenericProperty(object):
    """Generic property converter.

    Uses zope.xmlpickle to (de-)serialise the data.

    """

    zope.interface.implements(
        zeit.cms.content.interfaces.IGenericDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.IField)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        try:
            xml = lxml.etree.fromstring(value)
        except (lxml.etree.XMLSyntaxError), e:
            # Caputure generic xml errors reliably.
            raise ValueError(str(e))
        if xml.tag != 'pickle':
            raise ValueError("Invalid pickle.")
        return zope.xmlpickle.loads(
            lxml.etree.tostring(xml))

    def toProperty(self, value):
        xml = lxml.etree.fromstring(zope.xmlpickle.dumps(value))
        return lxml.etree.tounicode(xml)


class GenericCollectionProperty(GenericProperty):
    """Generic tuple property converter.

    Uses zope.xmlpickle to (de-)serialise the data.

    """

    zope.interface.implementsOnly(
        zeit.cms.content.interfaces.IDAVPropertyConverter)
    zope.component.adapts(zope.schema.interfaces.ICollection,
                          zope.interface.Interface)

    def __init__(self, context, value_type):
        self.context = context
        self.value_type = value_type
        self.content_converter = None

    def fromProperty(self, value):
        value = super(GenericCollectionProperty, self).fromProperty(value)
        if self.content_converter is not None:
            type_ = type(zope.proxy.removeAllProxies(value))
            value = type_(self.content_converter.fromProperty(item)
                          for item in value)
        return value

    def toProperty(self, value):
        if self.content_converter is not None:
            type_ = type(zope.proxy.removeAllProxies(value))
            value = type_(self.content_converter.toProperty(item)
                          for item in value)
        return super(GenericCollectionProperty, self).toProperty(value)


def mapProperties(interface, namespace, names, use_default=False,
                  writeable=WRITEABLE_ON_CHECKIN):
    vars = sys._getframe(1).f_locals
    for name in names:
        field = interface[name]
        mapProperty(field, namespace, name, vars, use_default=use_default,
                    writeable=writeable)


def mapProperty(field, namespace, name=None, vars=None, use_default=False,
                writeable=WRITEABLE_ON_CHECKIN):
    if vars is None:
        vars = sys._getframe(1).f_locals

    if name is None:
        name = field.__name__

    vars[name] = DAVProperty(field, namespace, name, use_default=use_default,
                             writeable=writeable)


def findProperty(class_, name, namespace):
    for attribute in dir(class_):
        prop = getattr(class_, attribute)
        if not isinstance(prop, DAVProperty):
            continue
        if prop.name == name and prop.namespace == namespace:
            return prop
    return None


class DAVPropertiesAdapter(grokcore.component.Adapter):

    grokcore.component.context(zeit.cms.repository.interfaces.IDAVContent)
    grokcore.component.baseclass()

    def __new__(cls, context):
        # Trusted adapter
        instance = object.__new__(cls)
        instance.__parent__ = context
        if zope.security.proxy.removeSecurityProxy(context) is context:
            # Context is unwrapped. Basically do nothing special here.
            instance.__init__(context)
            return instance
        # Context is wrapped. Unwrap and wrap adapter
        context = zope.security.proxy.removeSecurityProxy(context)
        instance.__init__(context)
        instance = zope.security.adapter.assertLocation(instance, context)
        return zope.security.proxy.ProxyFactory(instance)


@grokcore.component.adapter(DAVPropertiesAdapter)
@grokcore.component.implementer(zeit.connector.interfaces.IWebDAVProperties)
def dav_properties_for_dav_properties_adapter(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
