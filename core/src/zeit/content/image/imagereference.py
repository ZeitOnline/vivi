# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$


import zope.component
import zope.interface

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
        for image in values:
            image_element = self.xml(instance).makeelement('image')

            # XXX this is quite hairy; shouldn't we use adapters?
            if zeit.content.image.interfaces.IImage.providedBy(image):
                image_element.set('src', image.uniqueId)
                image_element.set('type', image.contentType.split('/')[-1])
            elif zeit.content.image.interfaces.IImageGroup.providedBy(image):
                image_element.set('base-id', image.uniqueId)
            else:
                raise ValueError("%r is not an image." % image)

            image_metadata = zeit.content.image.interfaces.IImageMetadata(
                image)
            expires = image_metadata.expires
            if expires:
                expires = expires.isoformat()
                image_element.set('expires', expires)
            image_element.bu = image_metadata.caption or ''
            image_element.copyright = image_metadata.copyrights
            self.xml(instance)['head'].append(image_element)

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
