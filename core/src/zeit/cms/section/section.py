from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.interfaces import ICMSContent
from zeit.cms.section.interfaces import (
    ISection, ISectionMarker, IRessortSection)
import grokcore.component as grok
import os.path
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zope.container.contained
import zope.interface
import zope.security.proxy


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
    # Dear Zope, why is ContainedProxy not a zope.proxy?
    content = zope.container.contained.getProxiedObject(content)

    for iface in zope.interface.providedBy(content):
        if issubclass(iface, ISectionMarker):
            zope.interface.noLongerProvides(content, iface)

    # Ressort markers take precedence over section markers (ZON-2507)
    markers = get_ressort_markers(content) or get_folder_markers(content)
    zope.interface.alsoProvides(content, *markers)


@grok.adapter(ICMSContent)
@grok.implementer(ISection)
def find_section(context):
    # Ressort markers take precedence over section markers (ZON-2507)
    return find_ressort_section(context) or find_folder_section(context)


def get_ressort_markers(content):
    section = find_ressort_section(content)
    if section is None:
        return []
    return get_markers_for_section(section, content)


def find_ressort_section(context):
    meta = ICommonMetadata(context, None)
    if meta is None:
        return None
    sm = zope.component.getSiteManager()
    return sm.adapters.lookup(
        (zope.interface.providedBy(context),), IRessortSection,
        name=meta.ressort)


def get_folder_markers(content):
    section = find_folder_section(content)
    return get_markers_for_section(section, content)


def find_folder_section(context):
    candidate = context
    while candidate is not None:
        if ISection.providedBy(candidate):
            break
        candidate = parent_folder(candidate)
    if candidate is None:
        return None
    # We don't support the case that a folder signifies more than one section,
    # but we probably don't want to.
    for iface in zope.interface.providedBy(candidate):
        if issubclass(iface, ISection):
            return iface


def parent_folder(content):
    if not content.uniqueId.startswith(zeit.cms.interfaces.ID_NAMESPACE):
        return None
    id = content.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '')
    if not id:
        return None
    if id.endswith('/'):
        id = id[:-1]
    return ICMSContent(zeit.cms.interfaces.ID_NAMESPACE + os.path.dirname(id))


def get_markers_for_section(section, content):
    if section is None:
        return []
    sm = zope.component.getSiteManager()
    result = []
    # Content-type specific markers come first, so they are treated as more
    # specific than the generic markers in adapter lookups.
    result.append(sm.adapters.lookup(
        (section,), ISectionMarker, name=zeit.cms.type.get_type(content)))
    result.append(sm.adapters.lookup((section,), ISectionMarker))
    return filter(None, result)
