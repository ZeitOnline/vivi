# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zope.component
import zope.interface

import zeit.cms.content.interfaces


class RelatedBase(object):

    zope.interface.implements(
        zeit.cms.content.interfaces.IXMLRepresentation)
    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)

    path = lxml.objectify.ObjectPath('.head.references.reference')
    xml_reference_name = 'related'

    def __init__(self, context):
        self.context = context

    # IXMLRepresentation

    @rwproperty.getproperty
    def xml(self):
        self._assure_tree()
        xml = self.path.find(self._get_xml())
        return xml.getparent()

    @rwproperty.setproperty
    def xml(self, value):
        self.path.setattr(self._get_xml(), value)

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
            related_element = zope.component.getAdapter(
                related,
                zeit.cms.content.interfaces.IXMLReference,
                name=self.xml_reference_name)
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

    def _assure_tree(self):
        try:
            xml = self.path.find(self._get_xml())
        except AttributeError:
            self.path.setattr(self._get_xml(), None)

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
        reference.set('year', unicode(metadata.year))
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
