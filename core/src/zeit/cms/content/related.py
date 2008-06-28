# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.interfaces
import zeit.cms.checkout.interfaces


class RelatedBase(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IXMLRepresentation)
    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)

    path = lxml.objectify.ObjectPath('.head.references.reference')
    xml_reference_name = 'related'

    def __init__(self, context):
        self.context = self.__parent__ = context

    # IXMLRepresentation

    @rwproperty.getproperty
    def xml(self):
        if self.path.hasattr(self._get_xml()):
            xml = self.path(self._get_xml()).getparent()
        else:
            self.path.setattr(self._get_xml(), None)
            xml = self.path(self._get_xml()).getparent()
            self.path.setattr(self._get_xml(), ())

        return xml

    @rwproperty.setproperty
    def xml(self, value):
        self.path.setattr(self._get_xml(), value)
        self.context._p_changed = True

    # Helper methods (used in subclasses)

    def _get_related(self):
        related = []
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for element in self._get_related_nodes():
            unique_id = self._get_unique_id(element)
            if unique_id is None:
                continue
            try:
                content = repository.getContent(unique_id)
            except (ValueError, KeyError):
                continue
            related.append(content)
        return tuple(related)

    def _set_related(self, values):
        elements = []
        for related in values:
            __traceback_info__ = (self.context.uniqueId, related.uniqueId,)
            related_element = zope.component.queryAdapter(
                related,
                zeit.cms.content.interfaces.IXMLReference,
                name=self.xml_reference_name)
            if related_element is None:
                raise ValueError(
                    ("Could not create xml reference '%s' for %s which "
                     "is referenced in %s.") % (
                         self.xml_reference_name,
                         related.uniqueId, self.context.uniqueId))

            elements.append(related_element)
        self.xml = elements

    def _get_unique_id(self, element):
        # XXX This is rather strange as the data is produced by adapters
        # but read out here quite hard coded.
        return element.get('href')

    def _get_related_nodes(self):
        try:
            return self.path.find(self._get_xml())
        except AttributeError:
            return []

    def _get_xml(self):
        return zope.security.proxy.removeSecurityProxy(self.context.xml)


class RelatedContent(RelatedBase):
    """Adapter which stores related content in xml."""

    zope.interface.implements(zeit.cms.content.interfaces.IRelatedContent)

    @rwproperty.getproperty
    def related(self):
        return self._get_related()

    @rwproperty.setproperty
    def related(self, value):
        return self._set_related(value)


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.cms.content.interfaces.IRelatedContent)
def related_from_template(context):
    return RelatedContent(context)


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLReference)
@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
def BasicReference(context):
    reference = lxml.objectify.E.reference()
    reference.set('type', 'intern')
    reference.set('href', context.uniqueId)

    metadata = zeit.cms.content.interfaces.ICommonMetadata(context, None)
    if metadata is not None:
        if metadata.year:
            reference.set('year', unicode(metadata.year))
        if metadata.volume:
            reference.set('issue', unicode(metadata.volume))
        reference['title'] = metadata.teaserTitle
        reference['description'] = metadata.teaserText

        reference.append(lxml.objectify.E.short(
            lxml.objectify.E.title(metadata.shortTeaserTitle),
            lxml.objectify.E.text(metadata.shortTeaserText)))
        reference.append(lxml.objectify.E.homepage(
            lxml.objectify.E.title(metadata.hpTeaserTitle),
            lxml.objectify.E.text(metadata.hpTeaserText)))

    return reference


def related(content, catalog):
    """Index support for relation catalog."""
    related = zeit.cms.content.interfaces.IRelatedContent(content, None)
    if related is None:
        return None
    return related.related


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_related_on_checkin(context, event):
    """Update the related metadata before checkin."""
    related = zeit.cms.content.interfaces.IRelatedContent(context, None)
    if related is None:
        return
    related_list = related.related
    if related_list:
        related.related = related_list
