# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import UserDict
import itertools
import lxml.etree
import lxml.objectify
import pkg_resources
import stabledict
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.related.interfaces
import zeit.cms.related.related
import zeit.cms.type
import zeit.cms.workflow.interfaces
import zeit.content.cp.interfaces
import zope.container.contained
import zope.interface
import zope.lifecycleevent


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

    type = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'type', zeit.content.cp.interfaces.ICenterPage['type'])

    zeit.cms.content.dav.mapProperties(
        zeit.content.cp.interfaces.ICenterPage,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('header_image',))

    def __getitem__(self, key):
        xml = self.editable_areas[key](self.xml['body'])[0]
        area = zope.component.getMultiAdapter(
            (self, xml),
            zeit.content.cp.interfaces.IArea,
            name=key)
        return zope.container.contained.contained(area, self, key)

    def updateMetadata(self, content):
        for entry in self.xml.xpath('//block[@href="%s"]' % content.uniqueId):
            updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(content)
            updater.update(entry)


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


@zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_centerpage_on_checkin(context, event):
    for content in zeit.content.cp.interfaces.ICMSContentIterable(context):
        context.updateMetadata(content)


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
    feed = zeit.content.cp.interfaces.ICPFeed(context)
    items = list(feed.items)

    for item in zeit.cms.syndication.interfaces.IReadFeed(context):
        if item not in items:
            items.insert(0, item)

    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.cp')
    max_items = config['cp-feed-max-items']
    while len(items) > max_items:
        del items[-1]

    feed.items = items
