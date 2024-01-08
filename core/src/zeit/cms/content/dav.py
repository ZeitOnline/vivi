import datetime
import functools
import logging
import re
import sys
import time

import grokcore.component as grok
import lxml.etree
import pendulum
import zope.app.security.interfaces
import zope.component
import zope.event
import zope.proxy
import zope.publisher.browser
import zope.schema.interfaces
import zope.xmlpickle

from zeit.cms.content.interfaces import WRITEABLE_ON_CHECKIN
import zeit.cms.content.caching
import zeit.cms.content.interfaces
import zeit.cms.content.liveproperty
import zeit.cms.grok
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.connector.interfaces


logger = logging.getLogger(__name__)
PROPERTY_REGISTRY = {}


class DAVProperty:
    """Descriptor that stores value in WebDAV properties and performs type
    conversion according to the given schema field."""

    def __init__(self, field, namespace, name, use_default=False, writeable=WRITEABLE_ON_CHECKIN):
        self.field = field
        self.namespace = namespace
        self.name = name
        if use_default:
            self.missing_value = field.default
        else:
            self.missing_value = field.missing_value
        # We cannot use a getUtility here, because this happens on import
        # time. We haven't got CA then.
        (
            zeit.cms.content.liveproperty.LiveProperties.register_live_property(
                name, namespace, writeable
            )
        )
        PROPERTY_REGISTRY[(name, namespace)] = self

    def __get__(self, instance, class_, properties=None):
        __traceback_info = (instance,)  # noqa
        if instance is None:
            return self
        fact = functools.partial(self.__fetch__, instance, class_, properties)
        uniqueId = getattr(instance, 'uniqueId', None) or (
            getattr(getattr(instance, 'context', None), 'uniqueId', None)
        )
        if properties is None and uniqueId is not None:
            key = self.field.__name__, self.namespace, self.name
            return zeit.cms.content.caching.get(uniqueId, key=key, factory=fact, suffix='.meta')
        else:
            return fact()

    def __fetch__(self, instance, class_, properties=None):
        if properties is None:
            properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        dav_value = properties.get(
            (self.name, self.namespace), zeit.connector.interfaces.DeleteProperty
        )

        if zope.proxy.removeAllProxies(dav_value) is zeit.connector.interfaces.DeleteProperty:
            value = self.missing_value
        else:
            field = self.field.bind(instance)
            __traceback_info__ = (instance, field, field.__name__, dav_value)
            try:
                converter = zope.component.getMultiAdapter(
                    (field, properties), zeit.cms.content.interfaces.IDAVPropertyConverter
                )
                value = converter.fromProperty(dav_value)
            except (ValueError, zope.schema.ValidationError) as e:
                value = self.field.default
                if zeit.cms.interfaces.ICMSContent.providedBy(instance):
                    unique_id = instance.uniqueId
                else:
                    unique_id = repr(instance)
                logger.warning(
                    'Could not parse DAV property value %r for '
                    '%s.%s at %s [%s: %r]. Using default %r instead.'
                    % (
                        dav_value,
                        instance.__class__.__name__,
                        self.name,
                        unique_id,
                        e.__class__.__name__,
                        e.args,
                        value,
                    )
                )

        return value

    def __set__(self, instance, value):
        """Set the value to webdav properties."""
        read_properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        old_value = read_properties.get((self.name, self.namespace))
        if value is None:
            dav_value = zeit.connector.interfaces.DeleteProperty
        else:
            field = self.field.bind(instance)
            converter = zope.component.getMultiAdapter(
                (field, read_properties), zeit.cms.content.interfaces.IDAVPropertyConverter
            )
            dav_value = converter.toProperty(value)

        write_properties = zeit.cms.interfaces.IWebDAVWriteProperties(instance)
        write_properties[(self.name, self.namespace)] = dav_value

        zope.event.notify(
            zeit.cms.content.interfaces.DAVPropertyChangedEvent(
                instance, self.namespace, self.name, old_value, dav_value, self.field
            )
        )


@zope.component.adapter(
    zope.interface.Interface, zeit.cms.content.interfaces.IDAVPropertyChangedEvent
)
def notify_cms_content_property_change(context, event):
    """Notify ICMSContent object about a property change.

    When a content object is adapted to extend functionality it is common to
    have an adapter to IWebDAVProperties from the adapter. In this case the
    original object would not be notified about changes.

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
            content,
            event.property_namespace,
            event.property_name,
            event.old_value,
            event.new_value,
            event.field,
        )
    )


@zope.component.adapter(
    zope.schema.interfaces.IFromUnicode, zeit.connector.interfaces.IWebDAVReadProperties
)
@zope.interface.implementer(zeit.cms.content.interfaces.IGenericDAVPropertyConverter)
class UnicodeProperty:
    def __init__(self, context, content):
        self.context = context

    def fromProperty(self, value):
        # Convert to unicode. We need to do that because lxml puts out an
        # ascii-str when the value has only 7bit characters. While this is an
        # optimisation in lxml we *need* a unicode here. If the value contains
        # 8 bit chars this is supposed to break.
        value = str(value)
        return self.context.fromUnicode(value)

    def toProperty(self, value):
        return str(value)


@zope.component.adapter(
    zope.schema.interfaces.IChoice, zeit.connector.interfaces.IWebDAVReadProperties
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
def ChoiceProperty(context, content):
    return zope.component.getMultiAdapter(
        (context, context.vocabulary, content), zeit.cms.content.interfaces.IDAVPropertyConverter
    )


@zope.component.adapter(
    zope.schema.interfaces.IChoice,
    zope.schema.interfaces.IIterableSource,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class ChoicePropertyWithIterableSource:
    def __init__(self, context, source, content):
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


@zope.component.adapter(
    zope.schema.interfaces.IChoice,
    zope.app.security.interfaces.IPrincipalSource,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class ChoicePropertyWithPrincipalSource:
    def __init__(self, context, source, content):
        self.context = context
        self.source = source

    def fromProperty(self, value):
        if value in self.source:
            return str(value)
        raise ValueError(value)

    def toProperty(self, value):
        return str(value)


DUMMY_REQUEST = zope.publisher.browser.TestRequest()


@zope.component.adapter(
    zope.schema.interfaces.IChoice,
    zeit.cms.content.sources.IObjectSource,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class ChoicePropertyWithObjectSource:
    def __init__(self, context, source, content):
        self.context = context
        self.source = source

    @property
    def terms(self):
        return zope.component.getMultiAdapter(
            (self.source, DUMMY_REQUEST), zope.browser.interfaces.ITerms
        )

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


@zope.component.adapter(
    zope.schema.interfaces.IChoice,
    zope.schema.interfaces.IIterableVocabulary,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class ChoicePropertyWithIterableVocabulary:
    def __init__(self, context, vocabulary, content):
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


@zope.component.adapter(zope.schema.Bool, zeit.connector.interfaces.IWebDAVReadProperties)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class BoolProperty:
    def __init__(self, context, content):
        self.context = context

    def fromProperty(self, value):
        if value.lower() in ('yes', 'true'):
            return True
        return False

    def toProperty(self, value):
        if value:
            return 'yes'
        return 'no'


@zope.component.adapter(
    zope.schema.interfaces.IDatetime, zeit.connector.interfaces.IWebDAVReadProperties
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class DatetimeProperty:
    def __init__(self, context, content):
        self.context = context

    def fromProperty(self, value):
        if not value:
            return None
        # We have _mostly_ iso8601, but some old content has the format
        # "Thu, 13 Mar 2008 13:48:37 GMT", so we use a lenient parser.
        date = pendulum.parse(value, strict=False)
        return date.in_tz('UTC')

    def toProperty(self, value):
        if value is None:
            return ''
        if value.tzinfo is None:
            raise ValueError('%r has no timezone information' % value)
        return value.isoformat()


@zope.component.adapter(
    zope.schema.interfaces.IDate, zeit.connector.interfaces.IWebDAVReadProperties
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class DateProperty:
    def __init__(self, context, content):
        self.context = context

    def fromProperty(self, value):
        if not value:
            return None
        return datetime.date(*(time.strptime(value, '%Y-%m-%d')[0:3]))

    def toProperty(self, value):
        if value is None:
            return ''
        return value.isoformat()


@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
@zope.component.adapter(
    zope.schema.interfaces.ICollection, zeit.connector.interfaces.IWebDAVReadProperties
)
def CollectionProperty(context, content):
    return zope.component.queryMultiAdapter(
        (context, context.value_type, content), zeit.cms.content.interfaces.IDAVPropertyConverter
    )


@zope.component.adapter(
    zope.schema.interfaces.ICollection,
    zope.schema.interfaces.ITextLine,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class CollectionTextLineProperty:
    SPLIT_PATTERN = re.compile(r'(?!\\);')

    def __init__(self, context, value_type, content):
        self.context = context
        self.value_type = value_type
        self.content = content
        self._type = context._type
        if isinstance(self._type, tuple):
            # XXX this is way hacky
            self._type = self._type[0]

    def fromProperty(self, value):
        typ = zope.component.getMultiAdapter(
            (self.value_type, self.content), zeit.cms.content.interfaces.IDAVPropertyConverter
        )
        result = []
        start = 0
        while value:
            found = value.find(';', start)
            if found > 0 and value[found - 1] == '\\':
                start = found + 1
                continue
            if found > 0:
                item = value[:found]
                value = value[found + 1 :]
            else:
                item = value
                value = ''
            item = item.replace('\\;', ';').replace('\\\\', '\\')
            item = typ.fromProperty(item)
            result.append(item)

        return self._type(result)

    def toProperty(self, value):
        typ = zope.component.getMultiAdapter(
            (self.value_type, self.content), zeit.cms.content.interfaces.IDAVPropertyConverter
        )
        result = []
        for item in value:
            item = typ.toProperty(item)
            result.append(item.replace('\\', '\\\\').replace(';', '\\;'))
        return ';'.join(result)


@zope.component.adapter(
    zeit.cms.content.interfaces.IChannelField, zeit.connector.interfaces.IWebDAVReadProperties
)
class ChannelProperty(UnicodeProperty):
    def fromProperty(self, value):
        # Cannot call super since CombinationField has no `fromUnicode`
        value = str(value)
        return tuple(value.split(' ')) if ' ' in value else (value, None)

    def toProperty(self, value):
        value = ' '.join([x for x in value if x])
        return super().toProperty(value)


# Since CollectionTextLineProperty only applies to value_type TextLine,
# we have to register it again so it picks up value_type IChannelField.
@zope.component.adapter(
    zope.schema.interfaces.ICollection,
    zeit.cms.content.interfaces.IChannelField,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class CollectionChannelProperty(CollectionTextLineProperty):
    pass


@zope.component.adapter(
    zope.schema.interfaces.IField, zeit.connector.interfaces.IWebDAVReadProperties
)
@zope.interface.implementer(zeit.cms.content.interfaces.IGenericDAVPropertyConverter)
class GenericProperty:
    """Generic property converter.

    Uses zope.xmlpickle to (de-)serialise the data.

    """

    def __init__(self, context, content):
        self.context = context

    def fromProperty(self, value):
        try:
            xml = lxml.etree.fromstring(value)
        except lxml.etree.XMLSyntaxError as e:
            # Caputure generic xml errors reliably.
            raise ValueError(str(e))
        if xml.tag != 'pickle':
            raise ValueError('Invalid pickle.')
        return zope.xmlpickle.loads(value)

    def toProperty(self, value):
        xml = lxml.etree.fromstring(zope.xmlpickle.dumps(value))
        return lxml.etree.tounicode(xml)


@zope.component.adapter(
    zope.schema.interfaces.ICollection,
    zope.interface.Interface,
    zeit.connector.interfaces.IWebDAVReadProperties,
)
@zope.interface.implementer_only(zeit.cms.content.interfaces.IDAVPropertyConverter)
class GenericCollectionProperty(GenericProperty):
    """Generic tuple property converter.

    Uses zope.xmlpickle to (de-)serialise the data.
    """

    def __init__(self, context, value_type, content):
        self.context = context
        self.value_type = value_type
        self.content_converter = None

    def fromProperty(self, value):
        value = super().fromProperty(value)
        if self.content_converter is not None:
            type_ = type(zope.proxy.removeAllProxies(value))
            value = type_(self.content_converter.fromProperty(item) for item in value)
        return value

    def toProperty(self, value):
        if self.content_converter is not None:
            type_ = type(zope.proxy.removeAllProxies(value))
            value = type_(self.content_converter.toProperty(item) for item in value)
        return super().toProperty(value)


def mapProperties(interface, namespace, names, use_default=False, writeable=WRITEABLE_ON_CHECKIN):
    """Create DAVProperty descriptors for all given names of the interface.
    Convenience to map several properties, if they use the same namespace
    and the python name is the same as the DAV property name.
    """
    vars = sys._getframe(1).f_locals
    for name in names:
        field = interface[name]
        mapProperty(field, namespace, name, vars, use_default=use_default, writeable=writeable)


def mapProperty(
    field, namespace, name=None, vars=None, use_default=False, writeable=WRITEABLE_ON_CHECKIN
):
    if vars is None:
        vars = sys._getframe(1).f_locals

    if name is None:
        name = field.__name__

    vars[name] = DAVProperty(field, namespace, name, use_default=use_default, writeable=writeable)


def findProperty(class_, name, namespace):
    for attribute in dir(class_):
        prop = getattr(class_, attribute)
        if not isinstance(prop, DAVProperty):
            continue
        if prop.name == name and prop.namespace == namespace:
            return prop
    return None


class DAVPropertiesAdapter(zeit.cms.grok.TrustedAdapter):
    grok.context(zeit.cms.repository.interfaces.IDAVContent)
    grok.baseclass()


@grok.adapter(DAVPropertiesAdapter)
@grok.implementer(zeit.connector.interfaces.IWebDAVProperties)
def dav_properties_for_dav_properties_adapter(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
