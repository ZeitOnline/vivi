# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict
import gocept.async
import lxml.etree
import pkg_resources
import stabledict
import zeit.cms.content.adapter
import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zope.container.contained
import zope.interface
import zope.lifecycleevent


class CenterPage(zeit.cms.content.metadata.CommonMetadata,
                 UserDict.DictMixin):
    """XXX docme"""

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage)

    default_template = pkg_resources.resource_string(__name__,
                                                     'cp-template.xml')
    editable_areas = stabledict.StableDict(
        [('lead', lxml.etree.XPath('region[@area="lead"]')),
         ('informatives', lxml.etree.XPath('region[@area="informatives"]')),
         ('teaser-mosaic', lxml.etree.XPath('cluster[@area="teaser-mosaic"]')),
        ])

    keys = editable_areas.keys
    __contains__ = editable_areas.__contains__

    def __getitem__(self, key):
        xml = self.editable_areas[key](self.xml['body'])[0]
        area = zope.component.getMultiAdapter(
            (self, xml),
            zeit.content.cp.interfaces.IArea,
            name=key)
        return zope.container.contained.contained(area, self, key)


centerpageFactory = zeit.cms.content.adapter.xmlContentFactory(CenterPage)


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'centerpage-2009')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage)(resourceFactory)


_test_helper_cp_changed = False


class CMSContentIterable(object):

    zope.component.adapts(zeit.content.cp.interfaces.ICenterPage)
    zope.interface.implements(zeit.content.cp.interfaces.ICMSContentIterable)

    def __init__(self, context):
        self.context = context

    def __iter__(self):
        for area in self.context.values():
            for content in zeit.content.cp.interfaces.ICMSContentIterable(area):
                yield content


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
