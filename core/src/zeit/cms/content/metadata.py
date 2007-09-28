# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.property


class KeywordsProperty(object):

    def __init__(self):
        self.path = lxml.objectify.ObjectPath('.head.keywordset.keyword')

    def __get__(self, instance, class_):
        tree = instance.xml
        taxonomy = self.taxonomy
        keywords = []
        try:
            keyword_set = self.path.find(tree)[:]
        except AttributeError:
            # no keywords
            keyword_set = []

        for keyword_node in keyword_set:
            rdf_id = unicode(keyword_node)
            keyword = taxonomy[rdf_id]
            keywords.append(keyword)

        return tuple(keywords)

    def __set__(self, instance, value):
        tree = instance.xml
        for keyword in self.path.find(tree, []):
            keyword.getparent().remove(keyword)
        self.path.setattr(tree, [keyword.code for keyword in value])
        for keyword in self.path.find(tree, []):
            keyword.set('source', 'manual')

    @property
    def taxonomy(self):
        return zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)


class CommonMetadata(object):

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('year', 'volume', 'ressort', 'serie', 'copyrights',
         'page'))

    # tuple/set doesn't work with webdav, yet
    #zeit.cms.content.dav.mapProperty(
    #    zeit.cms.content.interfaces.ICommonMetadata['authors'],
    #    zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
    #    'author')

    keywords = KeywordsProperty()

    authors = zeit.cms.content.property.MultipleAttributeProperty(
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'author')

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
