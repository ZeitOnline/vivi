from zeit.cms.i18n import MessageFactory as _
from zeit.cms.redirect.interfaces import IRenameInfo
from zeit.connector.search import SearchVar
from zeit.content.cp.interfaces import TEASER_ID_NAMESPACE
import collections
import copy
import gocept.cache.property
import gocept.lxml.interfaces
import grokcore.component as grok
import itertools
import lxml.etree
import pkg_resources
import xml.sax.saxutils
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.related.related
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.edit.body
import zeit.edit.container
import zeit.edit.interfaces
import zope.interface
import zope.lifecycleevent
import zope.proxy
import zope.security.proxy


BODY_NAME = 'body'


def create_delegate(name):
    def delegate(self, *args, **kw):
        return getattr(self.body, name)(*args, **kw)
    return delegate


class CenterPage(zeit.cms.content.metadata.CommonMetadata):

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = pkg_resources.resource_string(__name__,
                                                     'cp-template.xml')

    # We want to delegate only IContainer itself, not any inherited interfaces;
    # due to the read/write interface split, we need to express this manually.
    DELEGATE_METHODS = (
        set(zeit.edit.interfaces.IContainer)
        - set(zeit.cms.content.interfaces.IXMLRepresentation)
        - set(zope.container.interfaces.IContained)
        - set(zeit.edit.interfaces.IElement)
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

    header_image = zeit.cms.content.property.SingleResource(
        '.head.header_image',
        xml_reference_name='image', attributes=('base-id', 'src'))

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
        unique_ids = u' or '.join(['@href=%s' % xml.sax.saxutils.quoteattr(x)
                                  for x in possible_ids])
        # @uniqueId is for free teasers only, and those can't be renamed.
        query = u'//block[@uniqueId={id} or {unique_ids}]'.format(
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

    _cached_areas = gocept.cache.property.TransactionBoundCache(
        '_v_cached_areas', collections.OrderedDict)

    def _fill_area_cache(self):
        if not self._cached_areas:
            for region in self.body.values():
                for area in region.values():
                    self._cached_areas[area.__name__] = area

    _area_teasered_content = gocept.cache.property.TransactionBoundCache(
        '_v_area_teasered_content', dict)

    def teasered_content_above(self, current_area):
        self._fill_area_cache()
        seen = set()
        for area in self._cached_areas.values():
            if area == current_area:
                return seen
            if area not in self._area_teasered_content:
                self._area_teasered_content[area] = set(
                    zeit.content.cp.interfaces.ITeaseredContent(area))
            seen.update(self._area_teasered_content[area])
        return seen

    _area_manual_content = gocept.cache.property.TransactionBoundCache(
        '_v_area_manual_content', dict)

    def manual_content_below(self, current_area):
        self._fill_area_cache()
        seen = set()
        below = False
        for area in self._cached_areas.values():
            if area == current_area:
                below = True
            if not below:
                continue
            if area not in self._area_manual_content:
                # Probably not worth a separate adapter (like
                # ITeaseredContent), since the use case is pretty
                # specialised.
                self._area_manual_content[area] = set(
                    zeit.content.cp.blocks.teaser.extract_manual_teasers(
                        area))
            seen.update(self._area_manual_content[area])
        return seen


class CenterPageType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = CenterPage
    interface = zeit.content.cp.interfaces.ICenterPage
    title = _('Centerpage 2009')
    type = 'centerpage-2009'


class Body(zeit.edit.container.Base,
           grok.MultiAdapter):

    grok.implements(zeit.content.cp.interfaces.IBody)
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
        return super(Body, self).__getitem__(key)


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
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(*[
        zeit.content.cp.interfaces.ICMSContentIterable(block)
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
    for content in zeit.content.cp.interfaces.ICMSContentIterable(context):
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


class Feed(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implements(zeit.content.cp.interfaces.ICPFeed)

    # The feed items are ordered chronologically descending,
    # so the XSLT can just get the first n items to build the actual feed.
    items = zeit.cms.content.reference.MultiResource(
        '.feed.reference', 'related')

    def set_items_and_supress_errors(self, items):
        # XXX copy&paste from MultiResource.__set__, is there a better way to
        # do this?
        prop = type(self).items
        references = prop.references(self)
        value = tuple(
            references.create(x, suppress_errors=True) for x in items)
        super(zeit.cms.content.reference.MultiResource, prop).__set__(
            self, value)
        prop.update_metadata(self, suppress_errors=True)


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_feed_items(context, event):
    if not event.publishing:
        # This event should only happen while publishing. It used to be on
        # BeforePublish, but since that requires another checkin/checkout
        # cycle, and the centerpage is cycled during publish anyway, we can
        # register it like this and avoid the additional cycle.
        return
    feed = zeit.content.cp.interfaces.ICPFeed(context)
    feed.items = extract_feed_items(context)


def extract_feed_items(context):
    feed = zeit.content.cp.interfaces.ICPFeed(context)
    items = []
    check_items = []
    for item in feed.items:
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(item):
            check_item = item.original_content
        else:
            check_item = item
        items.append(item)
        check_items.append(check_item)

    teasers = zeit.content.cp.interfaces.ITeaseredContent(context)
    for item in teasers:
        if zeit.content.cp.interfaces.IXMLTeaser.providedBy(item):
            if item.original_content in check_items:
                continue
        elif item in check_items:
            continue
        items.insert(0, item)

    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')
    while len(items) > int(config['cp-feed-max-items']):
        del items[-1]

    return items


def has_changed(context):
    context = zope.proxy.removeAllProxies(context)
    if context._p_jar is None:
        # If there no jar, no change will have been marked.
        return True
    return context._p_changed


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
    # XXX This method duplicates the XML structure from cp-template.xml
    root = getattr(ElementMaker, context.xml.tag)(**context.xml.attrib)
    root.append(copy.copy(context.xml.head))
    root.append(lxml.objectify.E.body(
        lxml.objectify.E.cluster(
            zeit.content.cp.interfaces.IRenderedXML(context['lead']),
            zeit.content.cp.interfaces.IRenderedXML(context['informatives']),
            **context.xml.body.cluster.attrib),
        zeit.content.cp.interfaces.IRenderedXML(context['teaser-mosaic']),
    ))
    _render_feed(root)
    return root


def _render_feed(root):
    # Performance optimization: Since automatic CPs are populated with (sorted)
    # queries, there is not much point in trying to preserve a "historical
    # ordering" (i.e. when each article first appeared on the CP). Thus we can
    # simply copy the XML references of the teaser blocks into the feed,
    # instead of running the automatic queries *again*.
    feed = ElementMaker.feed()
    root.append(feed)
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')
    for i, teaser in enumerate(root.xpath(
            '//container[@cp:type="teaser"]/block', namespaces=NSMAP)):
        if i > config['cp-feed-max-items']:
            break
        item = copy.copy(teaser)
        item.tag = 'reference'
        item.set('type', 'intern')
        del item.attrib['uniqueId']
        feed.append(item)


@grok.adapter(zeit.content.cp.interfaces.ICP2015)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    root = getattr(ElementMaker, context.xml.tag)(
        **context.xml.attrib)
    root.append(copy.copy(context.xml.head))
    body = lxml.objectify.E.body()
    root.append(body)
    for region in context.body.values():
        body.append(zeit.content.cp.interfaces.IRenderedXML(region))
    _render_feed(root)
    return root


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def mark_cp_on_checkout(context, event):
    if (zeit.content.cp.interfaces.ICP2009.providedBy(context)
        or zeit.content.cp.interfaces.ICP2015.providedBy(context)):
        return
    zope.interface.alsoProvides(context, zeit.content.cp.interfaces.ICP2015)


@grok.subscribe(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckoutEvent)
def prevent_mismatched_checkout(context, event):
    other_iface = zeit.content.cp.interfaces.ICP2009
    current_iface = zeit.content.cp.interfaces.ICP2015
    if other_iface.providedBy(context):
        raise zeit.cms.checkout.interfaces.CheckinCheckoutError(
            context.uniqueId, _(
                'The centerpage ${uniqueId} is of type ${content_type},'
                ' but this vivi handles ${current_type}.', mapping={
                    'uniqueId': context.uniqueId,
                    'content_type': other_iface.__name__,
                    'current_type': current_iface.__name__,
                }))
