# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface

import zeit.cms.content.interfaces


class RelatedObjectsProperty(object):

    path = lxml.objectify.ObjectPath('.head.references.reference')

    def __get__(self, instance, class_):
        if instance is None:
            return class_
        related = []
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for element in self.related_elements(instance):
            unique_id = self.get_unique_id(element)
            try:
                content = repository.getContent(unique_id)
            except (ValueError, KeyError):
                continue
            related.append(content)
        return tuple(related)

    def __set__(self, instance, values):
        elements = []
        for related in values:
            related_element = zeit.cms.content.interfaces.IXMLReference(
                related).xml
            elements.append(related_element)
        self.path.setattr(self.xml(instance), elements)

    def related_elements(self, instance):
        try:
            container = self.path.find(self.xml(instance))
        except AttributeError:
            return []
        return list(container)

    def get_unique_id(self, element):
        # XXX This is rather strange as the data is produced by adapters
        # but read out here quite hard coded.
        return element.get('href')

    def xml(self, instance):
        return zope.security.proxy.removeSecurityProxy(
            zeit.cms.content.interfaces.IXMLRepresentation(instance).xml)


class RelatedContent(object):

    zope.interface.implements(zeit.cms.content.interfaces.IRelatedContent)
    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)

    related = RelatedObjectsProperty()

    def __init__(self, context):
        self.context = context


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.cms.content.interfaces.IRelatedContent)
def related_from_template(context):
    return RelatedContent(context)


@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
@zope.component.adapter(zeit.cms.content.interfaces.IRelatedContent)
def related_xml_representation(context):
    return context.context


class BasicReference(object):

    zope.interface.implements(zeit.cms.content.interfaces.IXMLReference)
    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)

    def __init__(self, context):
        self.context = context

    @property
    def xml(self):
        reference = lxml.objectify.XML('<reference/>')
        reference.set('type', 'intern')
        reference.set('href', self.context.uniqueId)

        metadata = zeit.cms.content.interfaces.ICommonMetadata(self.context,
                                                               None)
        if metadata is not None:
            reference.set('year', unicode(metadata.year))
            reference.set('issue', unicode(metadata.volume))
            reference['title'] = metadata.teaserTitle
            reference['description'] = metadata.teaserText

        return reference
