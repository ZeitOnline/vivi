# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.interfaces import ICMSContent
from zeit.cms.section.interfaces import ISection, ISectionMarker
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


def apply_markers(content):
    for iface in zope.interface.providedBy(content):
        if issubclass(ISectionMarker, iface):
            zope.interface.noLongerProvides(content, iface)
    section = ISection(content, None)
    if section is None:
        return
    for iface in get_section_markers(section, content):
        zope.interface.alsoProvides(content, iface)


def get_section_markers(section, content):
    section_ifaces = [x for x in zope.interface.providedBy(section)
                      if issubclass(x, ISection)]
    if not section_ifaces:
        return []
    sm = zope.component.getSiteManager()
    result = []
    # XXX unclear whether we really want to support the case that a folder
    # signifies more than one section
    for iface in section_ifaces:
        result.append(sm.adapters.lookup((iface,), ISectionMarker))
        result.append(sm.adapters.lookup(
            (iface,), ISectionMarker, name=zeit.cms.type.get_type(content)))
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
    id = content.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '')
    if not id:
        return None
    if id.endswith('/'):
        id = id[:-1]
    return ICMSContent(zeit.cms.interfaces.ID_NAMESPACE + os.path.dirname(id))
