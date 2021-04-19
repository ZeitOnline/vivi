from zeit.cms.content.cache import writeabledict
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.redirect.interfaces import IRenameInfo
from zeit.content.cp.interfaces import TEASER_ID_NAMESPACE
import collections
import copy
import gocept.cache.property
import gocept.lxml.interfaces
import grokcore.component as grok
import itertools
import lxml.etree
import xml.sax.saxutils
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.interfaces
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.content.cp.interfaces
import zeit.edit.body
import zeit.edit.container
import zeit.edit.interfaces
import zope.interface
import zope.lifecycleevent
import zope.security.proxy


BODY_NAME = 'body'


def create_delegate(name):
    def delegate(self, *args, **kw):
        return getattr(self.body, name)(*args, **kw)
    return delegate


@zope.interface.implementer(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.interfaces.IEditorialContent)
class CenterPage(zeit.cms.content.metadata.CommonMetadata):

    default_template = """\
<centerpage
  xmlns:cp="http://namespaces.zeit.de/CMS/cp"
  xmlns:py="http://codespeak.net/lxml/objectify/pytype"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <head/>
  <body/>
</centerpage>
"""

    # We want to delegate only IContainer itself, not any inherited interfaces;
    # due to the read/write interface split, we need to express this manually.
    DELEGATE_METHODS = (
        set(zeit.edit.interfaces.IContainer) -
        set(zeit.cms.content.interfaces.IXMLRepresentation) -
        set(zope.container.interfaces.IContained) -
        set(zeit.edit.interfaces.IElement)
    )

    @property
    def body(self):
        return zeit.content.cp.interfaces.IBody(self)

    for name in DELEGATE_METHODS:
        locals()[name] = create_delegate(name)

    _type_xml = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'type', zeit.content.cp.interfaces.ICenterPage['type'])
    _type_dav = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ICenterPage['type'],
        zeit.content.cp.interfaces.DAV_NAMESPACE, 'type')

    header_image = zeit.cms.content.reference.SingleResource(
        '.head.header_image',
        xml_reference_name='image')

    topiclink_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink_title',
        zeit.content.cp.interfaces.ICenterPage['topiclink_title'])

    topiclink_label_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_1'])

    topiclink_url_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_1'])

    topiclink_label_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_2'])

    topiclink_url_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_2'])

    topiclink_label_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_3'])

    topiclink_url_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_3'])

    og_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_title',
        zeit.content.cp.interfaces.ICenterPage['og_title'])

    og_description = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_description',
        zeit.content.cp.interfaces.ICenterPage['og_description'])

    og_image = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_image',
        zeit.content.cp.interfaces.ICenterPage['og_image'])

    def updateMetadata(self, content):
        # Note that this method is a shortcut using XPath to query instead of
        # instantiating all blocks and their content objects to find the
        # matching one (since that's probably too expensive). So actually the
        # updating should be performed by the respective blocks (or their
        # ReferenceProperties) and not by duplicating their
        # implementation/serialzation details here.

        # Support renaming (see doc/implementation/move.txt).
        possible_ids = set((
            content.uniqueId,) + IRenameInfo(content).previous_uniqueIds)
        unique_ids = ' or '.join(['@href=%s' % xml.sax.saxutils.quoteattr(x)
                                  for x in possible_ids])
        # @uniqueId is for free teasers only, and those can't be renamed.
        query = '//block[@uniqueId={id} or {unique_ids}]'.format(
            id=xml.sax.saxutils.quoteattr(content.uniqueId),
            unique_ids=unique_ids)
        for entry in self.xml.xpath(query):
            if entry.get('uniqueId', content.uniqueId) not in possible_ids:
                # ``entry`` is a free teaser, but ``content`` is the referenced
                # object. Skip it, since the metadata of the free teaser itself
                # is what counts.
                continue

            # migration code
            node = entry.find('references')
            if node is not None:
                entry.remove(node)

            if not entry.get('uniqueId', '').startswith(TEASER_ID_NAMESPACE):
                entry.set('href', content.uniqueId)
                entry.set('uniqueId', content.uniqueId)
            updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                content, None)
            if updater is not None:
                updater.update(entry)

            modified = zeit.cms.workflow.interfaces.IModified(content, None)
            if modified is not None:
                date = ''
                if modified.date_last_modified:
                    date = modified.date_last_modified.isoformat()
                entry.set('date-last-modified', date)

            publish_info = zeit.cms.workflow.interfaces.IPublishInfo(content,
                                                                     None)
            if publish_info is not None:
                date = ''
                if publish_info.date_first_released:
                    date = publish_info.date_first_released.isoformat()
                entry.set('date-first-released', date)
                date = ''
                if publish_info.date_last_published:
                    date = publish_info.date_last_published.isoformat()
                entry.set('date-last-published', date)

            lsc = zeit.cms.content.interfaces.ISemanticChange(content, None)
            if lsc is not None:
                date = ''
                if lsc.last_semantic_change:
                    date = lsc.last_semantic_change.isoformat()
                entry.set('last-semantic-change', date)

    @property
    def type(self):
        return self._type_xml

    @type.setter
    def type(self, value):
        self._type_xml = value
        self._type_dav = value

    cache = gocept.cache.property.TransactionBoundCache(
        '_v_cache', writeabledict)

    @property
    def cached_areas(self):
        key = 'cached_areas'
        if key not in self.cache:
            self.cache[key] = areas = []
            for region in self.body.values():
                for area in region.values():
                    areas.append(area)
        return self.cache[key]


class CenterPageType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = CenterPage
    interface = zeit.content.cp.interfaces.ICenterPage
    title = _('Centerpage 2009')
    type = 'centerpage-2009'


@grok.implementer(zeit.content.cp.interfaces.IBody)
class Body(zeit.edit.container.Base,
           grok.MultiAdapter):

    grok.provides(zeit.content.cp.interfaces.IBody)
    grok.adapts(zeit.content.cp.interfaces.ICenterPage,
                gocept.lxml.interfaces.IObjectified)

    __name__ = BODY_NAME
    _find_item = lxml.etree.XPath('./*[@area = $name]')
    _get_keys = lxml.etree.XPath('./*/@area')

    def _get_element_type(self, xml_node):
        return 'region'

    def __getitem__(self, key):
        if key in ['lead', 'informatives']:
            # backwards compatiblity for tests
            return self['feature'][key]
        return super().__getitem__(key)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.IBody)
def get_editable_body(centerpage):
    return zope.component.queryMultiAdapter(
        (centerpage,
         zope.security.proxy.removeSecurityProxy(centerpage.xml['body'])),
        zeit.content.cp.interfaces.IBody)


class BodyTraverser(zeit.edit.body.Traverser):

    grok.context(zeit.content.cp.interfaces.ICenterPage)
    body_name = BODY_NAME
    body_interface = zeit.content.cp.interfaces.IBody


_test_helper_cp_changed = False


@grok.adapter(zeit.edit.interfaces.IContainer)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.edit.interfaces.IElementReferences(block)
        for block in context.values()
        if block is not None])


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def cp_references(context):
    if context.header_image:
        return [context.header_image]
    return []


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_centerpage_on_checkin(context, event):
    if not zope.app.appsetup.appsetup.getConfigContext().hasFeature(
            'zeit.content.cp.update_metadata'):
        return
    for content in zeit.edit.interfaces.IElementReferences(context):
        context.updateMetadata(content)

    context.header_image = context.header_image


@zope.component.adapter(
    zope.interface.Interface,
    zope.lifecycleevent.IObjectModifiedEvent)
def modified_propagator(context, event):
    """Propagate a modified event to the center page for sublocation changes.
    """
    if zeit.content.cp.interfaces.ICenterPage.providedBy(context):
        return
    cp = zeit.content.cp.interfaces.ICenterPage(context, None)
    if cp is None:
        return
    zope.security.proxy.removeSecurityProxy(cp)._p_changed = True
    global _test_helper_cp_changed
    _test_helper_cp_changed = True


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.cms.workflow.interfaces.IPublishPriority)
def publish_priority_cp(context):
    if context.type == 'homepage':
        return zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE
    else:
        return zeit.cms.workflow.interfaces.PRIORITY_HIGH


NSMAP = collections.OrderedDict((
    ('cp', 'http://namespaces.zeit.de/CMS/cp'),
    ('py', 'http://codespeak.net/lxml/objectify/pytype'),
    ('xi', 'http://www.w3.org/2001/XInclude'),
    ('xsd', 'http://www.w3.org/2001/XMLSchema'),
    ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
))
ElementMaker = lxml.objectify.ElementMaker(nsmap=NSMAP)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    root = getattr(ElementMaker, context.xml.tag)(
        **context.xml.attrib)
    root.append(copy.copy(context.xml.head))
    body = lxml.objectify.E.body()
    root.append(body)
    for region in context.body.values():
        body.append(zeit.content.cp.interfaces.IRenderedXML(region))
    return root
