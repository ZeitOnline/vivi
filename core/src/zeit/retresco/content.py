from zeit.cms.repository.interfaces import AfterObjectConstructedEvent
import collections.abc
import grokcore.component as grok
import lxml.objectify
import os.path
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.author.author
import zeit.content.gallery.gallery
import zeit.content.gallery.interfaces
import zeit.content.link.link
import zeit.retresco.interfaces
import zope.component
import zope.schema.interfaces


@zope.interface.implementer(zeit.retresco.interfaces.ITMSContent)
class Content(object):

    uniqueId = None
    __name__ = None

    def __init__(self, data):
        self._tms_data = data
        self._tms_payload = data.get('payload', {})
        self._tms_payload_head = self._tms_payload.get('head', {})
        if 'url' in data:
            self.uniqueId = zeit.cms.interfaces.ID_NAMESPACE + data['url'][1:]
            self.__name__ = os.path.basename(self.uniqueId)
        self._build_xml_body()
        self._build_xml_head()
        self._build_xml_image()

    def _build_xml_body(self):
        E = lxml.objectify.E
        self.xml = E.content()
        for key, value in self._tms_payload.get('xml', {}).items():
            self.xml.append(getattr(E, key)(value))
        for container in ['body', 'teaser']:
            if container not in self._tms_payload:
                continue
            container = getattr(E, container)()
            self.xml.append(container)
            for key, value in self._tms_payload[container.tag].items():
                container.append(getattr(E, key)(value))

    def _build_xml_head(self):
        """head items must be handled explicitly, because of their structure
        and type conversion, which we need so they are properly queryable.

        We duplicate knowledge about the XML format here for performance
        reasons. If we wanted to use vivi APIs we first would have to resolve
        any referenced ICMSContent; instead we can create XML nodes directly.
        """
        if not self._tms_payload_head:
            return

        E = lxml.objectify.E
        head = E.head()
        self.xml.append(head)

        for id in self._tms_payload_head.get('authors', ()):
            # See zeit.content.author.reference.XMLReference
            head.append(E.author(href=id))

        for id in self._tms_payload_head.get('agencies', ()):
            # See zeit.cms.content.metadata.CommonMetadata.agencies
            head.append(E.agency(href=id))

        if 'covers' in self._tms_payload_head:
            # See zeit.content.volume.volume.Volume.set_cover
            covers = E.covers()
            self.xml.append(covers)
            for cover in self._tms_payload_head['covers']:
                covers.append(E.cover(**cover))

    def _build_xml_image(self):
        """Teaser images are usually contained in the document head and
        reference an image group.

        We allow ITMSContent factories to override this default behaviour.
        """
        image = self._get_teaser_image_xml()
        head = self.xml.find('head')
        if head is not None and image is not None:
            head.append(image)

    def _get_teaser_image_xml(self):
        image = self._tms_payload_head.get('teaser_image')
        if not image:
            return

        E = lxml.objectify.E

        # See zeit.content.image.imagegroup.XMLReference
        image = E.image(**{'base-id': image})
        fill_color = self._tms_payload_head.get('teaser_image_fill_color')
        if fill_color:
            image.set('fill_color', fill_color)
        return image


class TMSAuthor(Content, zeit.content.author.author.Author):

    def _build_xml_image(self):
        image = self._get_teaser_image_xml()
        if image is None:
            return
        image.tag = 'image_group'
        self.xml.append(image)


class TMSLink(Content, zeit.content.link.link.Link):
    pass


class TMSGallery(Content, zeit.content.gallery.gallery.Gallery):
    pass


@grok.adapter(TMSGallery)
@grok.implementer(zeit.content.gallery.interfaces.IVisibleEntryCount)
def gallery_entry_count(context):
    return context._tms_payload_head.get('visible_entry_count', 0)


@grok.implementer(zeit.cms.content.interfaces.IKPI)
class KPI(grok.Adapter):

    grok.context(zeit.retresco.interfaces.ITMSContent)
    FIELDS = zeit.retresco.interfaces.KPIFieldSource()

    def __init__(self, context):
        super().__init__(context)
        for prop, tms in self.FIELDS.items():
            setattr(self, prop, self.context._tms_data.get(tms, 0))


@grok.adapter(dict)
@grok.implementer(zeit.retresco.interfaces.ITMSContent)
def from_tms_representation(context):
    doc_type = context.get('doc_type', 'unknown')
    tms_typ = zope.component.queryUtility(
        zeit.retresco.interfaces.ITMSContent, name=doc_type)
    if tms_typ is None:
        typ = zope.component.queryUtility(
            zeit.cms.interfaces.ITypeDeclaration, name=doc_type)
        if typ is None:
            typ = zope.component.queryUtility(
                zeit.cms.interfaces.ITypeDeclaration, name='unknown')
        tms_typ = type(
            'TMS' + typ.factory.__name__, (Content, typ.factory), {})
        zope.component.provideUtility(
            tms_typ, zeit.retresco.interfaces.ITMSContent, name=doc_type)
    content = tms_typ(context)
    # XXX This event is not really applicable, since the whole point is that we
    # have no DAV resource here. However, it currently has only one handler,
    # `zeit.cms.type.restore_provided_interfaces_from_dav`, which only wants
    # the properties, which we do have. So we keep that protocol for now by
    # faking the expected API.
    zope.event.notify(AfterObjectConstructedEvent(
        content, FakeDAVResource(content, doc_type)))
    return content


# Not an adapter to IResource on purpose, since a) ITMSContent->IResource is
# not actually a semantically useful gesture and b) this only fakes enough to
# make properties work.
class FakeDAVResource(zeit.connector.resource.Resource):

    def __init__(self, content, type):
        super().__init__(content.uniqueId, content.__name__, type, 'fake data',
                         zeit.connector.interfaces.IWebDAVProperties(content))


@grok.implementer(zeit.retresco.interfaces.IElasticDAVProperties)
class WebDAVProperties(grok.Adapter, collections.abc.MutableMapping):

    grok.context(zeit.retresco.interfaces.ITMSContent)
    grok.provides(zeit.connector.interfaces.IWebDAVProperties)

    def __getitem__(self, key):
        name, namespace = key
        namespace = namespace.replace(
            zeit.retresco.interfaces.DAV_NAMESPACE_BASE, '', 1)
        name = quote_es_field_name(name)
        namespace = quote_es_field_name(namespace)
        return self.context._tms_payload[namespace][name]

    def keys(self):
        for ns, values in self.context._tms_payload.items():
            namespace = zeit.retresco.interfaces.DAV_NAMESPACE_BASE + ns
            for name in values:
                yield (unquote_es_field_name(name),
                       unquote_es_field_name(namespace))

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        raise RuntimeError("Cannot write on ReadOnlyWebDAVProperties")

    def __setitem__(self, key, value):
        raise RuntimeError("Cannot write on ReadOnlyWebDAVProperties")


def quote_es_field_name(name):
    """Elasticsearch does not allow `.` in field names."""
    return name.replace('.', '__DOT__')


def unquote_es_field_name(name):
    return name.replace('__DOT__', '.')


def davproperty_to_es(ns, name):
    ns = quote_es_field_name(
        ns.replace(zeit.retresco.interfaces.DAV_NAMESPACE_BASE, '', 1))
    name = quote_es_field_name(name)
    return ns, name


# DAVPropertyConverter below here ------------------------------


@grok.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class JSONType(grok.MultiAdapter):
    """Type converter for a json-native datatype."""

    grok.baseclass()

    def __init__(self, context, content):
        pass

    def fromProperty(self, value):
        return value

    def toProperty(self, value):
        return value


class Bool(JSONType):

    grok.adapts(
        zope.schema.Bool,  # IFromUnicode is parallel to IBool
        zeit.retresco.interfaces.IElasticDAVProperties)


class Int(JSONType):

    grok.adapts(
        zope.schema.Int,  # IFromUnicode is parallel to IInt
        zeit.retresco.interfaces.IElasticDAVProperties)


@grok.implementer(zeit.cms.content.interfaces.IDAVPropertyConverter)
class CollectionTextLine(grok.MultiAdapter):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.ITextLine,
        zeit.retresco.interfaces.IElasticDAVProperties)

    # Taken from zeit.cms.content.dav.CollectionTextLineProperty
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
            (self.value_type, self.content),
            zeit.cms.content.interfaces.IDAVPropertyConverter)
        return self._type([typ.fromProperty(x) for x in value])

    def toProperty(self, value):
        typ = zope.component.getMultiAdapter(
            (self.value_type, self.content),
            zeit.cms.content.interfaces.IDAVPropertyConverter)
        return [typ.toProperty(x) for x in value]


class CollectionChoice(CollectionTextLine):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zope.schema.interfaces.IChoice,
        zeit.retresco.interfaces.IElasticDAVProperties)


class CollectionChannels(CollectionTextLine):

    grok.adapts(
        zope.schema.interfaces.ICollection,
        zeit.cms.content.interfaces.IChannelField,
        zeit.retresco.interfaces.IElasticDAVProperties)
