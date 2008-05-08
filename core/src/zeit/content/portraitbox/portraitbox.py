# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zope.interface

import zeit.cms.content.property
import zeit.cms.content.xmlsupport

import zeit.content.portraitbox.interfaces


class Portraitbox(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.portraitbox.interfaces.IPortraitbox)

    default_template = (
        u'<container layout="artbox" label="portrait" '
        u'xmlns:py="http://codespeak.net/lxml/objectify/pytype" />')

    name = zeit.cms.content.property.ObjectPathProperty('.title')
    text = zeit.cms.content.property.Structure('.text')
    image = zeit.cms.content.property.SingleResource(
        '.image', xml_reference_name='image', attributes=('base_id', 'src'))



resource_factory = zope.component.adapter(
    zeit.content.portraitbox.interfaces.IPortraitbox)(
        zeit.cms.content.adapter.xmlContentToResourceAdapterFactory(
            'portraitbox'))


# Adapt resource to CMSContent
portraitbox_factory = zeit.cms.content.adapter.xmlContentFactory(Portraitbox)
