from zeit.cms.i18n import MessageFactory as _
from zeit.content.cp.interfaces import TEASER_ID_NAMESPACE
import grokcore.component
import urlparse
import uuid
import xml.sax.saxutils
import z3c.flashmessage.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.cmscontent
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.redirect.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class XMLTeaser(zope.container.contained.Contained,
                zeit.cms.content.xmlsupport.Persistent):

    zope.interface.implements(zeit.content.cp.interfaces.IXMLTeaser)

    teaserSupertitle = zeit.cms.content.property.ObjectPathProperty(
        '.supertitle',
        zeit.cms.content.interfaces.ICommonMetadata['teaserSupertitle'])
    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.title',
        zeit.cms.content.interfaces.ICommonMetadata['teaserTitle'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.text',
        zeit.cms.content.interfaces.ICommonMetadata['teaserText'])

    _free_teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', '{http://namespaces.zeit.de/CMS/cp}free-teaser',
        zeit.content.cp.interfaces.IXMLTeaser['free_teaser'])

    # The uniqueId of the content object we are referencing
    _href = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'href')
    # For free teasers, the special teaser uniqueId
    _uniqueId = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'uniqueId')

    # Migration notice: Before we introduced the uniqueId/href convention for
    # VIV-322, the 'uniqueId' attribute was unused, the content uniqueId was
    # stored in the '{http://namespaces.zeit.de/CMS/link}href' attribute, and
    # the 'href' attribute contained either the teaser-uniqueId or the
    # content-uniqueId, depending on the value of 'free-teaser'.

    def __init__(self, context, xml, name):
        self.xml = xml
        self.__name__ = name
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    def __getattr__(self, key):
        field = zeit.cms.content.interfaces.ICommonMetadata.get(key, None)
        if field is not None:
            if self.original_content is not None:
                return getattr(self.original_content, key)
            else:
                return field.default
        raise AttributeError(key)

    def __eq__(self, other):
        if not zeit.cms.interfaces.ICMSContent.providedBy(other):
            return False
        return self.uniqueId == other.uniqueId

    def __hash__(self):
        return hash(self.uniqueId)

    # When free_teaser is True, this is a http://teaser.vivi.zeit.de/ id.
    # When free_teaser is False this just points to the referenced article.
    @property
    def uniqueId(self):
        if self.free_teaser:
            return self._uniqueId
        else:
            return self._href

    @uniqueId.setter
    def uniqueId(self, value):
        self._href = value

    @property
    def free_teaser(self):
        return self._free_teaser

    @property
    def original_uniqueId(self):
        return self._href

    @original_uniqueId.setter
    def original_uniqueId(self, value):
        self._href = value

    @free_teaser.setter
    def free_teaser(self, value):
        if not value:
            raise ValueError("Free teaser cannot be switched off.")
        if self._free_teaser:
            return
        cp = zeit.content.cp.interfaces.ICenterPage(self.__parent__)

        self._uniqueId = TEASER_ID_NAMESPACE + '%s#%s' % (
            cp.uniqueId, str(uuid.uuid4()))
        self._free_teaser = True

    @property
    def original_content(self):
        return zeit.cms.interfaces.ICMSContent(self.original_uniqueId, None)


@grokcore.component.adapter(zeit.content.cp.interfaces.IXMLTeaser)
@grokcore.component.implementer(zeit.content.image.interfaces.IImages)
def images_for_xmlteaser(context):
    original = zeit.cms.interfaces.ICMSContent(context.original_uniqueId, None)
    return zeit.content.image.interfaces.IImages(original, None)


@grokcore.component.adapter(
    zeit.content.cp.interfaces.IXMLTeaser,
    zeit.cms.browser.interfaces.ICMSLayer,
    name='preview')
@grokcore.component.implementer(zope.interface.Interface)
def teaser_preview(context, request):
    original = zeit.cms.interfaces.ICMSContent(context.original_uniqueId, None)
    return zope.component.queryMultiAdapter(
        (original, request), name='preview')


@grokcore.component.adapter(basestring, name=TEASER_ID_NAMESPACE)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def resolve_teaser_unique_id(context):
    parsed = urlparse.urlparse(context)
    assert parsed.path.startswith('/')
    unique_id = parsed.path[1:]

    obj = zeit.cms.cmscontent.resolve_wc_or_repository(unique_id)

    if not zeit.content.cp.interfaces.ICenterPage.providedBy(obj):
        return
    # BBB Before the uniqueId/href convention, the teaser-uniqueId was stored
    # in the ``href`` attribute.
    block = obj.xml.xpath('//block[@uniqueId={id} or @href={id}]'.format(
                          id=xml.sax.saxutils.quoteattr(context)))
    if not block:
        return
    assert len(block) == 1
    block = block[0]
    return XMLTeaser(None, block, None)


@grokcore.component.adapter(
    zeit.content.cp.interfaces.ITeaserBlock,
    int)
@grokcore.component.implementer(
    zeit.content.cp.interfaces.IXMLTeaser)
def xml_teaser_for_block(context, index):
    try:
        xml = list(zope.security.proxy.removeSecurityProxy(
            context).iterentries())[index]
    except IndexError:
        return
    return zeit.content.cp.teaser.XMLTeaser(context, xml, str(index))


@zope.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.IObjectModifiedEvent)
def warn_about_free_teasers(context, event):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context)
    for obj in relating_objects:
        if zeit.content.cp.interfaces.ICenterPage.providedBy(obj):
            # BBB Before the uniqueId/href convention, the content uniqueId was
            # stored in the ``{link}href`` attribute.
            blocks = obj.xml.xpath(
                '//block[@cp:free-teaser '
                'and (@href={id} or @link:href={id})]'.format(
                    id=xml.sax.saxutils.quoteattr(context.uniqueId)),
                namespaces=dict(link='http://namespaces.zeit.de/CMS/link',
                                cp='http://namespaces.zeit.de/CMS/cp'))
            if blocks:
                # Close enough
                source = zope.component.getUtility(
                    z3c.flashmessage.interfaces.IMessageSource, name='session')
                source.send(_(
                    '"${name}" is referenced by a free teaser in "${teaser}"',
                    mapping=dict(name=context.uniqueId, teaser=obj.uniqueId)),
                    'error')
                break


class FakeRenameInfo(grokcore.component.Adapter):
    """IXMLTeaser cannot be renamed."""

    grokcore.component.context(zeit.content.cp.interfaces.IXMLTeaser)
    grokcore.component.implements(zeit.cms.redirect.interfaces.IRenameInfo)

    previous_uniqueIds = ()


class XMLTeaserLinkUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Set the link to the original article.

    XXX Kludgy. We need this since zeit.cms.syndication.feed unilaterally
    writes both a uniqueId and href attribute; a cleaner solution would be to
    use something like an IXMLReference adapter there and then have a specific
    adapter for IXMLTeasers.
    """

    zope.component.adapts(zeit.content.cp.interfaces.IXMLTeaser)

    def update(self, entry, suppress_errors=False):
        # We don't override `update_with_context` since we don't want to adapt
        # to `IXMLTeaser` which would create new teaser objects from articles.
        entry.set('href', self.context.original_uniqueId)


# LEGACY: Old teaser content type

class Teaser(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(
        zeit.content.cp.interfaces.ITeaser)

    original_content = zeit.cms.content.property.SingleResource(
        '.original_content')

    default_template = u"""\
        <teaser
          xmlns:py="http://codespeak.net/lxml/objectify/pytype">
        </teaser>
    """


class TeaserType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Teaser
    interface = zeit.content.cp.interfaces.ITeaser
    type = 'teaser'
    register_as_type = False


class TeaserLinkUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Set the link to the original article."""

    zope.component.adapts(zeit.content.cp.interfaces.ITeaser)

    def update(self, entry, suppress_errors=False):
        # We don't override `update_with_context` since we don't want to adapt
        # to `ITeaser` which would create new teaser objects from articles.
        entry.set('href', self.context.original_content.uniqueId)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_for_teaser(context):
    return zeit.content.image.interfaces.IImages(
        context.original_content, None)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def teaser_references(context):
    return [context.original_content]
