# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import UserDict
import itertools
import lxml.etree
import pkg_resources
import stabledict
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.type
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

    def __init__(self, xml_source=None):
        super(CenterPage, self).__init__(xml_source)
        self.type = zeit.content.cp.interfaces.ICenterPage['type'].missing_value

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
