# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify

import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.cms.content.related

import zeit.content.image.interfaces


class ImagesProperty(zeit.cms.content.related.RelatedObjectsProperty):

    path = lxml.objectify.ObjectPath('.head')
    relevant_tag = 'image'

    def get_unique_id(self, element):
        unique_id = element.get('base-id')
        if unique_id is None:
            unique_id = element.get('src')
        return unique_id


class ImagesAdapter(object):

    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    images = ImagesProperty()

    def __init__(self, context):
        self.context = context


@zope.component.adapter(ImagesAdapter)
@zope.interface.implementer(zeit.cms.content.interfaces.IXMLRepresentation)
def images_xml_representation(context):
    return context.context


@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
def images_from_template(context):
    return ImagesAdapter(context)


class FeedMetadataUpdater(object):
    """Add the *first* referenced image to the feed entry."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def update_entry(self, entry, content):
        images = zeit.content.image.interfaces.IImages(content, None)
        if images is None:
            return
        if not images.images:
            # No image referenced
            return
        # only add first image
        image = images.images[0]
        entry['image'] = zeit.cms.content.interfaces.IXMLReference(image).xml
