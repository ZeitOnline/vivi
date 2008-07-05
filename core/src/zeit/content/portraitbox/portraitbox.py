# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
"""Portraitbox."""

import lxml.objectify
import rwproperty

import zope.interface

import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.wysiwyg.html

import zeit.content.portraitbox.interfaces


class Portraitbox(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.portraitbox.interfaces.IPortraitbox)

    default_template = (
        u'<container layout="artbox" label="portrait" '
        u'xmlns:py="http://codespeak.net/lxml/objectify/pytype" />')

    name = zeit.cms.content.property.ObjectPathProperty('.block.title')
    text = zeit.cms.content.property.Structure('.block.text')
    image = zeit.cms.content.property.SingleResource(
        '.block.image', xml_reference_name='image',
        attributes=('base_id', 'src'))


resource_factory = zope.component.adapter(
    zeit.content.portraitbox.interfaces.IPortraitbox)(
        zeit.cms.content.adapter.xmlContentToResourceAdapterFactory(
            'portraitbox'))


# Adapt resource to CMSContent
portraitbox_factory = zeit.cms.content.adapter.xmlContentFactory(Portraitbox)



class PortraitboxHTMLContent(zeit.wysiwyg.html.HTMLContentBase):
    """HTML content of an article."""

    zope.component.adapts(zeit.content.portraitbox.interfaces.IPortraitbox)
    path = lxml.objectify.ObjectPath('.block.text')

    def get_tree(self):
        xml = zope.proxy.removeAllProxies(self.context.xml)
        text = self.path(xml, None)
        if text is None:
            self.path.setattr(xml, '')
            text = self.path(xml)
        elif len(text):
            for child in text.iterchildren():
                if child.tag == 'p':
                    break
            else:
                # There was no <p> node. Wrap the entire contents of text into
                # a new <p>
                children = [text.text]
                for child in text.getchildren():
                    children.append(child)
                    text.remove(child)
                text.append(lxml.objectify.E.p(*children))
        return text
