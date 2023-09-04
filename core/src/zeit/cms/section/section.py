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

    current_markers = [x for x in zope.interface.providedBy(content)
                       if issubclass(x, ISectionMarker)]
    # Ressort markers take precedence over section markers (ZON-2507)
    new_markers = (
        get_markers_for_section(find_ressort_section(content), content) or
        get_markers_for_section(find_folder_section(content), content))

    if current_markers != new_markers:
        for iface in current_markers:
            zope.interface.noLongerProvides(content, iface)
        zope.interface.alsoProvides(content, *new_markers)


@grok.adapter(ICMSContent)
@grok.implementer(ISection)
def find_section(context):
    # Ressort markers take precedence over section markers (ZON-2507)
    return find_ressort_section(context) or find_folder_section(context)


def find_ressort_section(context):
    meta = ICommonMetadata(context, None)
    if meta is None:
        return None
    sm = zope.component.getSiteManager()
    return sm.adapters.lookup(
        (zope.interface.providedBy(context),), IRessortSection,
        name=meta.ressort or '')


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
    return None


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
    # XXX We're seeing poisoning of the sm.adapters._v_lookup._cache in
    # production inside lovely.remotetask, which then causes
    # `lookup((IZONSection,), ISectionMarker)` to return None instead of
    # IZONContent. We cannot explain this (see BUG-505), so we work around it
    # by bypassing the cache here.
    sm = zope.component.getSiteManager()
    lookup = sm.adapters._v_lookup._uncached_lookup
    result = []
    # Content-type specific markers come first, so they are treated as more
    # specific than the generic markers in adapter lookups.
    result.append(lookup(
        (section,), ISectionMarker, name=zeit.cms.type.get_type(content)))
    result.append(lookup((section,), ISectionMarker))
    return [x for x in result if x]
