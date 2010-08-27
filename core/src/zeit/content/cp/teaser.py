# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import urlparse
import uuid
import xml.sax.saxutils
import z3c.flashmessage.interfaces
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.interface


class XMLTeaser(zope.container.contained.Contained,
                zeit.cms.content.xmlsupport.Persistent):

    zope.interface.implements(zeit.content.cp.interfaces.IXMLTeaser)

    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.supertitle',
        zeit.cms.content.interfaces.ICommonMetadata['supertitle'])
    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.title',
        zeit.cms.content.interfaces.ICommonMetadata['teaserTitle'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.text',
        zeit.cms.content.interfaces.ICommonMetadata['teaserText'])

    _free_teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', '{http://namespaces.zeit.de/CMS/cp}free-teaser',
        zeit.content.cp.interfaces.IXMLTeaser['free_teaser'])

    # When free_teaser is True, this is a http://teaser.vivi.zeit.de/ id.
    # When free_teaser is False this just points to the referenced article.
    uniqueId = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'href')
    original_uniqueId = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', '{http://namespaces.zeit.de/CMS/link}href')


    def __init__(self, context, xml, name):
        self.xml = xml
        self.__name__ = name
        # Set parent last so we don't trigger a write.
        self.__parent__ = context

    def __getattr__(self, key):
        if key in zeit.cms.content.interfaces.ICommonMetadata:
            return None
        raise AttributeError(key)

    @property
    def free_teaser(self):
        return self._free_teaser

    @free_teaser.setter
    def free_teaser(self, value):
        if not value:
            raise ValueError("Free teaser cannot be switched off.")
        if self._free_teaser:
            return
        cp = zeit.content.cp.interfaces.ICenterPage(self.__parent__)

        self.original_uniqueId = self.uniqueId
        self.uniqueId = 'http://teaser.vivi.zeit.de/%s#%s' % (
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


@grokcore.component.adapter(
    basestring, name='http://teaser.vivi.zeit.de/')
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def resolve_teaser_unique_id(context):
    parsed = urlparse.urlparse(context)
    assert parsed.path.startswith('/')
    unique_id = parsed.path[1:]
    # Have a look into the workingcopy first
    wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
    obj = None
    for obj in wc.values():
        if not zeit.cms.interfaces.ICMSContent.providedBy(obj):
            continue
        if obj.uniqueId == unique_id:
            break
    else:
        obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
    if not zeit.content.cp.interfaces.ICenterPage.providedBy(obj):
        return
    block = obj.xml.xpath('//block[@href=%s]' %
                          xml.sax.saxutils.quoteattr(context))
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
            blocks = obj.xml.xpath(
                '//block[@link:href=%s and @cp:free-teaser]' % (
                    xml.sax.saxutils.quoteattr(context.uniqueId),),
                namespaces=dict(link='http://namespaces.zeit.de/CMS/link',
                                cp='http://namespaces.zeit.de/CMS/cp'))
            if blocks:
                # Close enough
                source = zope.component.getUtility(
                    z3c.flashmessage.interfaces.IMessageSource, name='session')
                source.send(
                    _('"${name}" is referenced by a free teaser in "${teaser}"',
                      mapping=dict(name=context.uniqueId,
                                   teaser=obj.uniqueId)),
                    'error')
                break


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

teaserFactory = zeit.cms.content.adapter.xmlContentFactory(Teaser)
resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'teaser')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.ITeaser)(resourceFactory)


class TeaserLinkUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Set the link to the original article."""

    zope.component.adapts(zeit.content.cp.interfaces.ITeaser)

    def update(self, entry):
        # We don't override `update_with_context` since we don't want to adapt
        # to `ITeaser` which would create new teaser objects from articles.
        entry.set('{http://namespaces.zeit.de/CMS/link}href',
                  self.context.original_content.uniqueId)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_for_teaser(context):
    return zeit.content.image.interfaces.IImages(
        context.original_content, None)


@zope.component.adapter(zeit.content.cp.interfaces.ITeaser)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def teaser_references(context):
    return [context.original_content]
