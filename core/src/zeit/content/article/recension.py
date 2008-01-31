# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface

import zeit.cms.content.property
import zeit.cms.content.xml
import zeit.content.article.interfaces


class BookRecensionContainer(object):

    zope.interface.implements(
        zeit.content.article.interfaces.IBookRecensionContainer)
    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context

    def __getitem__(self, index):
        return self._create_recension(self.entries[index])

    def __iter__(self):
        for node in self.entries:
            yield self._create_recension(node)

    def __len__(self):
        return len(self.entries)

    def append(self, recension):
        xml_repr = zeit.cms.content.interfaces.IXMLRepresentation(recension)
        self.context.xml['body'].append(xml_repr.xml)

    @property
    def entries(self):
        return lxml.objectify.ObjectPath(
        '.body.{http://namespaces.zeit.de/bibinfo}entry').find(
            self.context.xml, ())

    def _create_recension(self, node):
        recension = BookRecension()
        recension.xml = node
        return recension


class BookRecension(zeit.cms.content.xml.XMLRepresentationBase):
    """A recension for a book."""

    zope.interface.implements(zeit.content.article.interfaces.IBookRecension)

    default_template = u'<entry xmlns="http://namespaces.zeit.de/bibinfo"/>'

    authors = zeit.cms.content.property.SimpleMultiProperty(
        '.auth-info.author')
    title = zeit.cms.content.property.ObjectPathProperty('.title')
    genre = zeit.cms.content.property.ObjectPathProperty('.genre')
    info = zeit.cms.content.property.ObjectPathProperty('.info')
    category = zeit.cms.content.property.ObjectPathProperty('.category')
    age_limit = zeit.cms.content.property.ObjectPathProperty('.agelimit')
    original_language = zeit.cms.content.property.ObjectPathProperty(
        '.original_language')
    translator = zeit.cms.content.property.ObjectPathProperty(
        '.translator')
    publisher = zeit.cms.content.property.ObjectPathProperty(
        '.edition.publisher')
    location = zeit.cms.content.property.ObjectPathProperty(
        '.edition.location')
    year = zeit.cms.content.property.ObjectPathProperty(
        '.edition.year')
    media_type = zeit.cms.content.property.ObjectPathProperty(
        '.edition.mediatype')
    pages = zeit.cms.content.property.ObjectPathProperty(
        '.edition.pages')
    price = zeit.cms.content.property.ObjectPathProperty(
        '.edition.price')

    raw_data = u'Wird noch nicht eingelesen.'  # XXX
