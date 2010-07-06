# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
from zeit.cms.i18n import MessageFactory as _
from zeit.connector.search import SearchVar
import UserDict
import gocept.async
import grokcore.component
import itertools
import lxml.etree
import lxml.objectify
import pkg_resources
import stabledict
import zeit.cms.checkout.helper
import zeit.cms.checkout.interfaces
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.related.interfaces
import zeit.cms.related.related
import zeit.cms.sitecontrol.interfaces
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.cp.interfaces
import zope.container.contained
import zope.interface
import zope.lifecycleevent
import zope.proxy


class CenterPage(zeit.cms.content.metadata.CommonMetadata,
                 UserDict.DictMixin):

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = pkg_resources.resource_string(__name__,
                                                     'cp-template.xml')
    editable_areas = stabledict.StableDict(
        [('lead', lxml.etree.XPath('cluster/region[@area="lead"]')),
         ('informatives', lxml.etree.XPath('cluster/region[@area="informatives"]')),
         ('teaser-mosaic', lxml.etree.XPath('cluster[@area="teaser-mosaic"]')),
        ])

    keys = editable_areas.keys
    __contains__ = editable_areas.__contains__

    _type_xml = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'type', zeit.content.cp.interfaces.ICenterPage['type'])
    _type_dav = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ICenterPage['type'],
        zeit.content.cp.interfaces.DAV_NAMESPACE, 'type')

    header_image = zeit.cms.content.property.SingleResource(
        '.head.header_image',
        xml_reference_name='image', attributes=('base-id', 'src'))

    snapshot = zeit.cms.content.property.SingleResource(
        '.head.snapshot',
        xml_reference_name='image', attributes=('base-id', 'src'))

    def __getitem__(self, key):
        xml = self.editable_areas[key](self.xml['body'])[0]
        area = zope.component.getMultiAdapter(
            (self, xml),
            zeit.content.cp.interfaces.IArea,
            name=key)
        return zope.container.contained.contained(area, self, key)

    def updateMetadata(self, content):
        for entry in self.xml.xpath('//block[@href="%s"]' % content.uniqueId):
            # migration code
            node = entry.find('references')
            if node is not None:
                entry.remove(node)
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


class CenterPageType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = CenterPage
    interface = zeit.content.cp.interfaces.ICenterPage
    title = _('Centerpage 2009')
    type = 'centerpage-2009'


_test_helper_cp_changed = False


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    return itertools.chain(
        *[zeit.content.cp.interfaces.ICMSContentIterable(area)
          for area in context.values()])


@zope.component.adapter(zeit.content.cp.interfaces.ICenterPage)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def cp_references(context):
    cms_content = list(zeit.content.cp.interfaces.ICMSContentIterable(context))
    images = [context.header_image, context.snapshot]
    images = [x for x in images if x]
    return cms_content + images


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_centerpage_on_checkin(context, event):
    for content in zeit.content.cp.interfaces.ICMSContentIterable(context):
        context.updateMetadata(content)

    context.header_image = context.header_image
    context.snapshot = context.snapshot


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


class Feed(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implements(zeit.content.cp.interfaces.ICPFeed)

    path = lxml.objectify.ObjectPath('.feed.reference')

    # the feed items are ordered chronologically descending,
    # so the XSLT can just get the first n items to build the actual feed.
    items = property(zeit.cms.related.related.RelatedBase._get_related,
                     zeit.cms.related.related.RelatedBase._set_related)


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def update_feed_items(context, event):
    # The CP is cycled during publish but we need to do that again :(
    # Ignore conflicts during checkin here. It's almost impossible that
    # somebody else has changed the CP. Unfortunately there is no explicit test
    # for ignoring conflicts.
    with zeit.cms.checkout.helper.checked_out(
        context, events=False, ignore_conflicts=True) as co:
        if co is None:
            return
        feed = zeit.content.cp.interfaces.ICPFeed(co)
        items = []
        check_items = []
        for item in feed.items:
            if zeit.content.cp.interfaces.ITeaser.providedBy(item):
                check_item = item.original_content
            else:
                check_item = item
            items.append(item)
            check_items.append(check_item)

        for item in zeit.cms.syndication.interfaces.IReadFeed(context):
            if zeit.content.cp.interfaces.ITeaser.providedBy(item):
                if item.original_content in check_items:
                    continue
            elif item in check_items:
                continue
            items.insert(0, item)

        items_in_lead = len(zeit.cms.syndication.interfaces.IReadFeed(context))
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.cp')
        max_items = max(items_in_lead, int(config['cp-feed-max-items']))
        while len(items) > max_items:
            del items[-1]

        feed.items = items


def has_changed(context):
    context = zope.proxy.removeAllProxies(context)
    if context._p_jar is None:
        # If there no jar, no change will have been marked.
        return True
    return context._p_changed


class SiteControlTopicPages(grokcore.component.GlobalUtility):

    grokcore.component.implements(
        zeit.cms.sitecontrol.interfaces.ISitesProvider)
    grokcore.component.name('topicpage')

    def __iter__(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        type_index = SearchVar(
            'type', zeit.content.cp.interfaces.DAV_NAMESPACE)
        result = connector.search([type_index],
                                  type_index == 'topicpage')
        result = [zeit.cms.interfaces.ICMSContent(uid, None)
                  for uid, dummy in result]
        return (obj for obj in result if obj is not None)
