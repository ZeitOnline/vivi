# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zeit.cms.content.property
import zeit.cms.content.xml

import zeit.content.infobox.interfaces

class Infobox(zeit.cms.content.xml.XMLContentBase):

    default_template = u'<container layout="artbox" label="info"/>'

    supertitle = zeit.cms.content.property.ObjectPathProperty('.supertitle')

    @rwproperty.getproperty
    def contents(self):
        raise NotImplementedError

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
