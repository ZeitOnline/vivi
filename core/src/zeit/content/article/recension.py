# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface
import zope.security.proxy
import zope.publisher.interfaces

import z3c.traverser.interfaces

import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.content.article.interfaces




class BookRecensionContainer(object):

    zope.interface.implements(
        zeit.content.article.interfaces.IBookRecensionContainer,
        zope.location.interfaces.ILocation)
    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    def __init__(self, context):
        self.context = context
        self.__parent__ = context
        self.__name__ = 'recensions'


    def __getitem__(self, index):
        return self._create_recension(index, self.entries[index])

    def __iter__(self):
        for index, node in enumerate(self.entries):
            yield self._create_recension(index, node)

    def __len__(self):
        return len(self.entries)

    def append(self, recension):
        xml_repr = zeit.cms.content.interfaces.IXMLRepresentation(recension)
        self.xml['body'].append(xml_repr.xml)
        zope.security.proxy.removeSecurityProxy(
            self.context)._p_changed = True

    @property
    def entries(self):
        return lxml.objectify.ObjectPath(
            '.body.{http://namespaces.zeit.de/bibinfo}entry').find(
                self.xml, ())

    @property
    def xml(self):
        return zope.security.proxy.removeSecurityProxy(self.context.xml)

    def _create_recension(self, index, node):
        recension = BookRecension()
        recension.xml = node
        return zope.location.location.located(recension, self, unicode(index))


class BookRecension(zeit.cms.content.xmlsupport.XMLRepresentationBase):
    """Information about a book in a recension."""

    zope.interface.implements(
        zeit.content.article.interfaces.IBookRecension,
        zope.location.interfaces.ILocation)

    default_template = (
        u'<entry xmlns="http://namespaces.zeit.de/bibinfo" '
        u'xmlns:py="http://codespeak.net/lxml/objectify/pytype" />')


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

    __parent__ = None
    __name__ = None


class RecensionContainerTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if self.context.has_recensions:
            recensions = (
                zeit.content.article.interfaces.IBookRecensionContainer(
                    self.context))
            if name == recensions.__name__:
                return recensions
        raise zope.publisher.interfaces.NotFound(self.context, name, request)


class RecensionTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            index = int(name)
        except ValueError:
            pass
        else:
            try:
                return self.context[index]
            except IndexError:
                pass

        raise zope.publisher.interfaces.NotFound(self.context, name, request)


