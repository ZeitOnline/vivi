# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zope.interface

import zeit.cms.content.property
import zeit.cms.content.xml

import zeit.content.infobox.interfaces

class Infobox(zeit.cms.content.xml.XMLContentBase):

    zope.interface.implements(zeit.content.infobox.interfaces.IInfobox)

    default_template = u'<container layout="artbox" label="info"/>'

    supertitle = zeit.cms.content.property.ObjectPathProperty('.supertitle')

    @rwproperty.getproperty
    def contents(self):
        result = []
        for node in self.xml.findall('block'):
            result.append((unicode(node['title']),
                           unicode(node['text'])))
        return tuple(result)

    @rwproperty.setproperty
    def contents(self, value):
        xml = self.xml
        for node in xml.findall('block'):
            xml.remove(node)
        for title, text in value:
            block = lxml.objectify.E('block')
            xml.append(block)
            block['title'] = title
            block['text'] = text
        self._p_changed = True


resource_factory = zope.component.adapter(
    zeit.content.infobox.interfaces.IInfobox)(
        zeit.cms.content.adapter.xmlContentToResourceAdapterFactory('infobox'))


# Adapt resource to CMSContent
infobox_factory = zeit.cms.content.adapter.xmlContentFactory(Infobox)
