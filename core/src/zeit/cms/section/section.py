from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.interfaces import ICMSContent
from zeit.cms.section.interfaces import (
    ISection, ISectionMarker, IRessortSection)
import grokcore.component as grok
import os.path
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.interface


@grok.subscribe(
    ICMSContent, zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def mark_section_content_on_add(context, event):
    apply_markers(context)


@grok.subscribe(
    ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckoutEvent)
def mark_section_content_on_checkout(context, event):
    apply_markers(context)


@grok.subscribe(
    ICMSContent, zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def mark_section_content_on_checkin(context, event):
    apply_markers(context)


def apply_markers(content):
    content = zope.security.proxy.getObject(content)

    for iface in zope.interface.providedBy(content):
        if issubclass(iface, ISectionMarker):
            zope.interface.noLongerProvides(content, iface)

    # Ressort markers take precedence over section markers (ZON-2507)
    markers = get_ressort_markers(content) or get_folder_markers(content)
    zope.interface.alsoProvides(content, *markers)


def get_ressort_markers(content):
    meta = ICommonMetadata(content, None)
    if meta is None:
        return []
    sm = zope.component.getSiteManager()
    section = sm.adapters.lookup(
        (zope.interface.providedBy(content),), IRessortSection,
        name=meta.ressort)
    if section is None:
        return []
    return get_markers_for_section([section], content)


def get_folder_markers(content):
    section = ISection(content, None)
    # XXX unclear whether we really want to support the case that a folder
    # signifies more than one section.
    section_ifaces = [x for x in zope.interface.providedBy(section)
                      if issubclass(x, ISection)]
    return get_markers_for_section(section_ifaces, content)


def get_markers_for_section(section_ifaces, content):
    sm = zope.component.getSiteManager()
    result = []
    # Content-type specific markers come first, so they are treated as more
    # specific than the generic markers in adapter lookups.
    for iface in section_ifaces:
        result.append(sm.adapters.lookup(
            (iface,), ISectionMarker, name=zeit.cms.type.get_type(content)))
    for iface in section_ifaces:
        result.append(sm.adapters.lookup((iface,), ISectionMarker))
    return filter(None, result)


@grok.adapter(ICMSContent)
@grok.implementer(ISection)
def find_section(context):
    candidate = parent_folder(context)
    while candidate is not None:
        if ISection.providedBy(candidate):
            return candidate
        candidate = parent_folder(candidate)


def parent_folder(content):
    if not content.uniqueId.startswith(zeit.cms.interfaces.ID_NAMESPACE):
        return None
    id = content.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '')
    if not id:
        return None
    if id.endswith('/'):
        id = id[:-1]
    return ICMSContent(zeit.cms.interfaces.ID_NAMESPACE + os.path.dirname(id))
