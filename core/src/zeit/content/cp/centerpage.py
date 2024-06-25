import copy
import itertools

import gocept.cache.property
import grokcore.component as grok
import lxml.builder
import lxml.etree
import zope.interface
import zope.lifecycleevent
import zope.location.interfaces
import zope.security.proxy

from zeit.cms.content.cache import writeabledict
from zeit.cms.i18n import MessageFactory as _
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
import zeit.seo.seo


BODY_NAME = 'body'


@zope.interface.implementer(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.interfaces.IEditorialContent
)
class CenterPage(zeit.cms.content.metadata.CommonMetadata):
    default_template = """\
<centerpage xmlns:cp="http://namespaces.zeit.de/CMS/cp">
  <head/>
  <body/>
</centerpage>
"""

    @property
    def body(self):
        return zeit.content.cp.interfaces.IBody(self)

    _type_xml = zeit.cms.content.property.ObjectPathAttributeProperty(
        None, 'type', zeit.content.cp.interfaces.ICenterPage['type']
    )
    _type_dav = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ICenterPage['type'],
        zeit.content.cp.interfaces.DAV_NAMESPACE,
        'type',
    )

    topiclink_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink_title',
        zeit.content.cp.interfaces.ICenterPage['topiclink_title'],
    )

    topiclink_label_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_1'],
    )

    topiclink_url_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_1',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_1'],
    )

    topiclink_label_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_2'],
    )

    topiclink_url_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_2',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_2'],
    )

    topiclink_label_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_3'],
    )

    topiclink_url_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_3',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_3'],
    )

    topiclink_label_4 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_4',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_4'],
    )

    topiclink_url_4 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_4',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_4'],
    )

    topiclink_label_5 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_label_5',
        zeit.content.cp.interfaces.ICenterPage['topiclink_label_5'],
    )

    topiclink_url_5 = zeit.cms.content.property.ObjectPathProperty(
        '.head.topiclinks.topiclink.topiclink_url_5',
        zeit.content.cp.interfaces.ICenterPage['topiclink_url_5'],
    )

    liveblog_label_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_label_1',
        zeit.content.cp.interfaces.ICenterPage['liveblog_label_1'],
    )

    liveblog_url_1 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_url_1', zeit.content.cp.interfaces.ICenterPage['liveblog_url_1']
    )

    liveblog_label_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_label_2',
        zeit.content.cp.interfaces.ICenterPage['liveblog_label_2'],
    )

    liveblog_url_2 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_url_2', zeit.content.cp.interfaces.ICenterPage['liveblog_url_2']
    )

    liveblog_label_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_label_3',
        zeit.content.cp.interfaces.ICenterPage['liveblog_label_3'],
    )

    liveblog_url_3 = zeit.cms.content.property.ObjectPathProperty(
        '.head.liveblogs.liveblog_url_3', zeit.content.cp.interfaces.ICenterPage['liveblog_url_3']
    )

    og_title = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_title', zeit.content.cp.interfaces.ICenterPage['og_title']
    )

    og_description = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_description', zeit.content.cp.interfaces.ICenterPage['og_description']
    )

    og_image = zeit.cms.content.property.ObjectPathProperty(
        '.head.og_meta.og_image', zeit.content.cp.interfaces.ICenterPage['og_image']
    )

    @property
    def type(self):
        return self._type_xml

    @type.setter
    def type(self, value):
        self._type_xml = value
        self._type_dav = value

    cache = gocept.cache.property.TransactionBoundCache('_v_cache', writeabledict)

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
class Body(zeit.edit.container.Base, grok.MultiAdapter):
    grok.provides(zeit.content.cp.interfaces.IBody)
    grok.adapts(zeit.content.cp.interfaces.ICenterPage, zeit.cms.interfaces.IXMLElement)

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
        (centerpage, zope.security.proxy.removeSecurityProxy(centerpage.xml.find('body'))),
        zeit.content.cp.interfaces.IBody,
    )


class BodyTraverser(zeit.edit.body.Traverser):
    grok.context(zeit.content.cp.interfaces.ICenterPage)
    body_name = BODY_NAME
    body_interface = zeit.content.cp.interfaces.IBody


_test_helper_cp_changed = False


@grok.adapter(zeit.edit.interfaces.IContainer)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def cms_content_iter(context):
    return itertools.chain(
        *[
            zeit.edit.interfaces.IElementReferences(block)
            for block in context.values()
            if block is not None
        ]
    )


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.edit.interfaces.IElementReferences)
def centerpage_content_iter(context):
    return zeit.edit.interfaces.IElementReferences(context.body)


@zope.component.adapter(zope.interface.Interface, zope.lifecycleevent.IObjectModifiedEvent)
def modified_propagator(context, event):
    """Propagate a modified event to the center page for sublocation changes."""
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


NSMAP = {'cp': 'http://namespaces.zeit.de/CMS/cp'}
ElementMaker = lxml.builder.ElementMaker(nsmap=NSMAP)


@grok.adapter(zeit.content.cp.interfaces.ICenterPage)
@grok.implementer(zeit.content.cp.interfaces.IRenderedXML)
def rendered_xml(context):
    root = getattr(ElementMaker, context.xml.tag)(**context.xml.attrib)
    root.append(copy.copy(context.xml.find('head')))
    body = lxml.builder.E.body()
    root.append(body)
    for region in context.body.values():
        body.append(zeit.content.cp.interfaces.IRenderedXML(region))
    return root


class CpSEO(zeit.seo.seo.SEO):
    grok.provides(zeit.content.cp.interfaces.ICpSEO)

    enable_rss_tracking_parameter = zeit.cms.content.dav.DAVProperty(
        zeit.content.cp.interfaces.ICpSEO['enable_rss_tracking_parameter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'seo-enable-rss-tracking-parameter',
    )
