# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import lxml.objectify
import rwproperty

import zope.component
import zope.interface

import zeit.cms.checkout.interfaces
import zeit.cms.content.related
import zeit.cms.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.image.interfaces


class ImagesAdapter(zeit.cms.content.related.RelatedBase):

    zope.component.adapts(zeit.cms.content.interfaces.IXMLContent)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    path = lxml.objectify.ObjectPath('.head.image')
    xml_reference_name = 'image'

    @rwproperty.getproperty
    def images(self):
        return self._get_related()

    @rwproperty.setproperty
    def images(self, value):
        self._set_related(value)

    def _get_unique_id(self, element):
        unique_id = element.get('base-id')
        if unique_id is None:
            unique_id = element.get('src')
        return unique_id


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
        entry['image'] = zope.component.getAdapter(
            image,
            zeit.cms.content.interfaces.IXMLReference, name='image')


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_image_reference_on_checkin(context, event):
    images = zeit.content.image.interfaces.IImages(context, None)
    if images is None:
        return
    image_list = images.images
    if image_list:
        images.images = image_list
