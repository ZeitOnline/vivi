# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$


import zope.component
import zope.interface

import gocept.lxml.interfaces

import zeit.cms.repository.interfaces

import zeit.content.image.interfaces


class ImagesProperty(object):

    def __get__(self, instance, class_):
        if instance is None:
            return class_
        images = []
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        for image_element in self.image_elements(instance):
            # XXX This is rather strange as the data is produced by adapters
            # but read out here quite hard coded.
            unique_id = image_element.get('base-id')
            if unique_id is None:
                unique_id = image_element.get('src')
            try:
                content = repository.getContent(unique_id)
            except (ValueError, KeyError):
                continue
            images.append(content)
        return tuple(images)

    def __set__(self, instance, values):
        for element in self.image_elements(instance):
            element.getparent().remove(element)
        if not values:
            return
        head = self.xml(instance)['head']
        for image in values:
            image_element = gocept.lxml.interfaces.IObjectified(image)
            assert image_element.tag == 'image'  # safty belt.
            head.append(image_element)

    def image_elements(self, instance):
        return self.xml(instance)['head'].findall('image')

    def xml(self, instance):
        return zope.security.proxy.removeSecurityProxy(
            zeit.cms.content.interfaces.IXMLRepresentation(instance))


class ImagesAdapter(object):

    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    images = ImagesProperty()

    def __init__(self, context):
        self.context = context


@zope.component.adapter(ImagesAdapter)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
def images_xml_representation(context):
    return context.context.xml

@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_from_template(context):
    return ImagesAdapter(context)
