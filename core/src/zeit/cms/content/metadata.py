# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import lxml.etree
import gocept.lxml.objectify

import persistent
import zope.component

import zope.app.container.contained

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.property


class KeywordsProperty(zeit.cms.content.property.MultiPropertyBase):

    def __init__(self):
        super(KeywordsProperty, self).__init__('.head.keywordset.keyword')

    def __set__(self, instance, value):
        super(KeywordsProperty, self).__set__(instance, value)
        tree = instance.xml
        for keyword in self.path.find(tree, []):
            keyword.set('source', 'manual')

    def _element_factory(self, node, tree):
        taxonomy = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        rdf_id = unicode(node)
        return taxonomy[rdf_id]

    def _node_factory(self, entry, tree):
        return entry.code


class CommonMetadata(persistent.Persistent,
                     zope.app.container.contained.Contained):

    zope.interface.implements(
        zeit.cms.content.interfaces.IXMLContent,
        zeit.cms.content.interfaces.ICommonMetadata)

    uniqueId = None
    __name__ = None

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('serie', 'copyrights', 'year', 'volume', 'ressort', 'page'))

    authors = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['authors'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'author',
        use_default=True)

    keywords = KeywordsProperty()

    title = zeit.cms.content.property.ObjectPathProperty(
        '.body.title')
    subtitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.subtitle')
    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle')
    byline = zeit.cms.content.property.ObjectPathProperty(
        '.body.byline')

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.title')
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.text')

    shortTeaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.indexteaser.title')
    shortTeaserText = zeit.cms.content.property.ObjectPathProperty(
        '.indexteaser.text')


    default_template = None  # Define in subclasses

    def __init__(self, xml_source=None):
        if xml_source is None:
            if self.default_template is None:
                raise NotImplementedError(
                    "default_template needs to be set in subclasses")
            xml_source = StringIO.StringIO(self.default_template)
        self.xml = gocept.lxml.objectify.fromfile(xml_source)
